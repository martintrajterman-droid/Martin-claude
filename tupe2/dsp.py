"""Bloques de síntesis (osciladores, filtros, instrumentos, reverb). Todo es matemática: sin samples."""
import json
import math
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(11)

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


def place(buf, sig, start, gain=1.0):
    i = int(round(start * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def env_adsr(n, a, d, s, r, sus_len):
    """ADSR en muestras; sus_len = duración total antes del release (s)."""
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S = max(0, int(sus_len * SR) - A - D)
    e = np.concatenate([
        np.linspace(0, 1, max(A, 1), endpoint=False),
        np.linspace(1, s, max(D, 1), endpoint=False),
        np.full(S, s),
        np.linspace(s, 0, max(R, 1)),
    ])
    out = np.zeros(n)
    m = min(n, len(e))
    out[:m] = e[:m]
    return out


def svf(x, cutoff, q=0.7, mode="lp"):
    """Filtro de estado variable TPT (Zavalishin): estable con cutoff modulado."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    g = np.tan(np.pi * np.clip(cutoff, 20, SR * 0.45) / SR)
    k = 1.0 / q
    a1 = 1.0 / (1.0 + g * (g + k))
    a2 = g * a1
    a3 = g * a2
    ic1 = ic2 = 0.0
    out = np.empty_like(x)
    xl, a1l, a2l, a3l = x.tolist(), a1.tolist(), a2.tolist(), a3.tolist()
    for i in range(len(xl)):
        v0 = xl[i]
        v3 = v0 - ic2
        v1 = a1l[i] * ic1 + a2l[i] * v3
        v2 = ic2 + a2l[i] * ic1 + a3l[i] * v3
        ic1 = 2 * v1 - ic1
        ic2 = 2 * v2 - ic2
        out[i] = v2 if mode == "lp" else (v1 if mode == "bp" else v0 - k * v1 - v2)
    return out


def onepole_hp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x)
    prev_x = prev_y = 0.0
    for i, v in enumerate(x.tolist()):
        prev_y = a * (prev_y + v - prev_x)
        prev_x = v
        y[i] = prev_y
    return y


def saw(phase):
    return 2.0 * (phase - np.floor(phase + 0.5))


def polyblep_saw(freq, n, phase0=0.0):
    """Sierra con PolyBLEP: sin aliasing audible."""
    dt = np.broadcast_to(np.asarray(freq, dtype=float) / SR, (n,))
    ph = (phase0 + np.cumsum(dt)) % 1.0
    y = 2 * ph - 1
    m1 = ph < dt
    tt = ph[m1] / dt[m1]
    y[m1] -= tt + tt - tt * tt - 1
    m2 = ph > 1 - dt
    tt = (ph[m2] - 1) / dt[m2]
    y[m2] -= tt * tt + tt + tt + 1
    return y


# ----------------------------------------------------------------------------
# Instrumentos
# ----------------------------------------------------------------------------

def kick(length=0.5, punch=1.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 46 + 190 * np.exp(-t * 32) + 60 * np.exp(-t * 300)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = rng.standard_normal(n) * np.exp(-t * 900) * 0.35 * punch
    k = np.tanh((body + click) * 2.2) * 0.9
    return k


def clap():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    # tres micro-golpes + cola: así suena una palmada real
    e = np.zeros(n)
    for k, off in enumerate([0.0, 0.011, 0.022]):
        i = int(off * SR)
        e[i:] += np.exp(-(t[: n - i]) * (180 if k < 2 else 22))
    s = svf(noise * e, 1400, q=1.6, mode="bp") * 2.2
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * 0.35
    return np.tanh(s + tone)


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    # ruido metálico: suma de cuadradas inarmónicas (receta clásica 808) + ruido
    metal = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in [205.3, 304.4, 369.6, 522.7, 540, 800])
    x = metal * 0.15 + rng.standard_normal(n) * 0.6
    x = onepole_hp(x, 7000)
    return x * np.exp(-t * (14 if open_ else 90)) * 0.7


def riser(length, f0=300, f1=9000):
    n = int(length * SR)
    t = np.arange(n) / SR
    p = t / length
    noise = rng.standard_normal(n)
    cut = f0 * (f1 / f0) ** (p ** 1.6)
    s = svf(noise, cut, q=3.5, mode="bp")
    # tono ascendente debajo del ruido
    f = 110 * 2 ** (p * 3)
    tone = saw((np.cumsum(f) / SR) % 1.0) * 0.18
    return (s * 0.8 + tone) * (p ** 2.2)


def impact(length=3.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 32 + 90 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    burst = svf(rng.standard_normal(n), 2500 * np.exp(-t * 3) + 120, q=0.8) * np.exp(-t * 3.5)
    return np.tanh(sub * 1.6 + burst * 0.9)


def downlifter(length=1.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    p = t / length
    cut = 9000 * (200 / 9000) ** p
    return svf(rng.standard_normal(n), cut, q=2.5, mode="bp") * (1 - p) ** 1.5 * 0.9


def bass_note(note, length, cutoff_peak=900):
    n = int((length + 0.05) * SR)
    t = np.arange(n) / SR
    f = midi(note)
    osc = polyblep_saw(np.full(n, f), n) * 0.6 + polyblep_saw(np.full(n, f * 1.004), n) * 0.4
    sub = np.sin(2 * np.pi * f / 2 * t) * 0.9
    cut = 120 + cutoff_peak * np.exp(-t * 14)
    x = svf(osc, cut, q=1.8) + sub * 0.7
    e = env_adsr(n, 0.004, 0.08, 0.8, 0.04, length)
    return np.tanh(x * e * 1.6) * 0.8


def pluck(note, length=0.2, bright=1.0):
    n = int((length + 0.25) * SR)
    t = np.arange(n) / SR
    f = midi(note)
    sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + polyblep_saw(np.full(n, f * 1.003), n) * 0.5
    cut = 300 + 5200 * bright * np.exp(-t * 22)
    x = svf(sq, cut, q=1.3)
    return x * np.exp(-t * 9) * 0.5


def bell(note, length=1.2):
    """Campana FM (portadora 1 : moduladora 3.5) con índice que decae."""
    n = int(length * SR)
    t = np.arange(n) / SR
    fc = midi(note)
    idx = 2.2 * np.exp(-t * 6) + 0.25
    mod = np.sin(2 * np.pi * fc * 3.5 * t) * idx
    car = np.sin(2 * np.pi * fc * t + mod)
    shimmer = np.sin(2 * np.pi * fc * 2.0 * t + mod * 0.5) * 0.25
    return (car + shimmer) * np.exp(-t * 3.2) * 0.35


def supersaw(notes, length, cut_start, cut_end, detune=0.16, voices=7):
    n = int((length + 0.4) * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    for note in notes:
        f = midi(note)
        for v in range(voices):
            d = (v - (voices - 1) / 2) / ((voices - 1) / 2)   # -1..1
            fv = f * (1 + d * detune * 0.06)
            s = polyblep_saw(np.full(n, fv), n, phase0=rng.random())
            pan = 0.5 + d * 0.45
            L += s * math.cos(pan * math.pi / 2)
            R += s * math.sin(pan * math.pi / 2)
    t = np.arange(n) / SR
    p = np.clip(t / length, 0, 1)
    cut = cut_start * (cut_end / cut_start) ** p
    e = env_adsr(n, 0.02, 0.3, 0.85, 0.35, length)
    scale = 0.06 / len(notes) * 4
    return svf(L, cut, q=0.9) * e * scale, svf(R, cut, q=0.9) * e * scale


# ----------------------------------------------------------------------------
# Reverb: convolución con una respuesta al impulso sintética (ruido con decaimiento)
# ----------------------------------------------------------------------------

def synth_ir(length=2.4, decay=2.8, seed=0):
    r = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * decay)
    # oscurecer la cola: más agudos se pierden con el tiempo
    ir = svf(ir, 9000 * np.exp(-t * 1.4) + 600, q=0.6)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    return ir / np.sqrt(np.sum(ir ** 2))


def convolve(x, ir):
    n = len(x) + len(ir) - 1
    nf = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[: len(x)]
    return y


