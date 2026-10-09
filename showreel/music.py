"""
Banda sonora del showreel: sintetizada desde cero con numpy.
Sin samples: cada sonido es una ecuación (osciladores, ruido, envolventes, filtros).

128 BPM · 8 compases de 4/4 = exactamente 15.000 s.
Salida: music.wav (48 kHz, estéreo, 16 bit) + analysis.json (envolventes por frame
a 60 fps que usa la parte visual para reaccionar al audio real).
"""
import json
import math
import sys
import wave

import numpy as np

SR = 48000
BPM = 128.0
BEAT = 60.0 / BPM            # 0.46875 s
BAR = BEAT * 4               # 1.875 s
DUR = 15.0
N = int(SR * DUR)
FPS = 60
rng = np.random.default_rng(7)

t_all = np.arange(N) / SR


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


# ----------------------------------------------------------------------------
# Partitura
# ----------------------------------------------------------------------------
# Fa menor. Progresión por compás: Fm9 · Dbmaj9 · Ab(add9) · Eb6 (x2), cierre en Fm9.
PROG = [
    dict(root=41, pad=[56, 60, 63, 67], arp=[65, 68, 72, 75]),   # Fm9
    dict(root=37, pad=[56, 60, 63, 65], arp=[65, 68, 72, 77]),   # Dbmaj9
    dict(root=44, pad=[58, 60, 63, 68], arp=[63, 68, 72, 75]),   # Ab add9
    dict(root=39, pad=[55, 58, 63, 67], arp=[63, 67, 70, 74]),   # Eb
]
FINAL = dict(root=41, pad=[56, 60, 63, 67, 72], arp=[65, 68, 72, 75])

stems = {k: np.zeros(N) for k in ["kick", "clap", "hats", "bass", "arp", "bell", "fx"]}
padL = np.zeros(N)
padR = np.zeros(N)

# --- Bombo ----------------------------------------------------------------
kick_times = []
# compás 0: latidos sordos en negras (la "respiración" del punto en pantalla)
for b in range(4):
    kick_times.append((at(0, b), 0.55))
for bar in range(1, 7):
    for b in range(4):
        if bar == 3 and b == 3:
            continue  # hueco antes del drop
        kick_times.append((at(bar, b), 1.0))
kick_times.append((at(7, 0), 1.0))
K = kick()
for tt, g in kick_times:
    place(stems["kick"], K, tt, g)

# --- Palmas: 2 y 4 desde el compás 2; redoble de construcción en compás 3 ---
C = clap()
for bar in [2, 4, 5, 6]:
    for b in [1, 3]:
        place(stems["clap"], C, at(bar, b), 0.8)
place(stems["clap"], C, at(3, 1), 0.8)
# redoble en semicorcheas -> fusas, crescendo
roll = [at(3, 2 + i * 0.25) for i in range(4)] + [at(3, 3 + i * 0.125) for i in range(7)]
for i, tt in enumerate(roll):
    place(stems["clap"], C, tt, 0.25 + 0.6 * i / len(roll))

# --- Hi-hats --------------------------------------------------------------
HC, HO = hat(False), hat(True)
for bar in range(1, 7):
    for s in range(16):
        tt = at(bar, s * 0.25)
        if bar == 3 and s >= 12:
            continue
        if s % 4 == 2:
            place(stems["hats"], HO, tt, 0.55)
        elif bar >= 4 or s % 2 == 0:
            accent = 0.6 if s % 2 == 0 else 0.32
            place(stems["hats"], HC, tt, accent)

# --- Bajo: corcheas a contratiempo (el bombo ocupa la parte fuerte) -------
for bar in range(1, 7):
    ch = PROG[bar % 4]
    for b in range(4):
        if bar == 3 and b == 3:
            continue
        for half in [0.5]:
            note = ch["root"] + (12 if (b == 3 and bar >= 4) else 0)
            place(stems["bass"], bass_note(note, BEAT * 0.42, 1100 if bar >= 4 else 700), at(bar, b + half), 1.0)
# nota larga final
place(stems["bass"], bass_note(29, 1.6, 400), at(7, 0), 1.1)

# --- Arpegio pluck en semicorcheas ----------------------------------------
pattern = [0, 1, 2, 3, 2, 1, 2, 3, 0, 2, 1, 3, 2, 3, 1, 2]
for bar in range(1, 7):
    ch = PROG[bar % 4]
    for s in range(16):
        if bar == 3 and s >= 12:
            continue
        note = ch["arp"][pattern[s]] + (12 if (bar >= 4 and s % 8 == 7) else 0)
        bright = 0.45 + 0.55 * (s % 4 == 0) if bar < 4 else 1.0
        if bar == 1:
            bright *= 0.5 + 0.5 * s / 16
        place(stems["arp"], pluck(note, 0.1, bright), at(bar, s * 0.25), 0.55)

# --- Melodía de campana FM en el drop -------------------------------------
melody = [
    (4, 0.0, 77), (4, 0.75, 75), (4, 1.5, 72), (4, 2.5, 75), (4, 3.0, 77),
    (5, 0.0, 80), (5, 0.75, 77), (5, 1.5, 75), (5, 2.5, 72), (5, 3.25, 75),
    (6, 0.0, 75), (6, 0.75, 72), (6, 1.5, 68), (6, 2.0, 70), (6, 2.5, 72), (6, 3.0, 75), (6, 3.5, 79),
    (7, 0.0, 80),
]
for bar, beat, note in melody:
    place(stems["bell"], bell(note, 2.4 if bar == 7 else 1.1), at(bar, beat), 0.9 if bar < 7 else 1.2)

# --- Pad supersaw ---------------------------------------------------------
for bar in range(0, 7):
    ch = PROG[bar % 4]
    if bar == 0:
        l, r = supersaw(ch["pad"], BAR, 250, 1400)
        g = 0.7
    elif bar < 4:
        l, r = supersaw(ch["pad"], BAR, 700, 2200)
        g = 0.55
    else:
        l, r = supersaw(ch["pad"] + [ch["pad"][-1] + 12], BAR, 2500, 6000)
        g = 0.8
    place(padL, l, at(bar), g)
    place(padR, r, at(bar), g)
l, r = supersaw(FINAL["pad"], 1.7, 5000, 600)
place(padL, l, at(7), 0.9)
place(padR, r, at(7), 0.9)

# --- FX -------------------------------------------------------------------
place(stems["fx"], riser(BAR * 0.95, 200, 5000), 0.0, 0.5)
place(stems["fx"], riser(BAR * 1.0, 300, 11000), at(3), 0.75)
place(stems["fx"], impact(3.0), at(4), 0.9)
place(stems["fx"], downlifter(1.4), at(4), 0.35)
place(stems["fx"], riser(BAR * 0.5, 600, 9000), at(6, 2), 0.5)
place(stems["fx"], impact(2.0), at(7), 1.0)
# "tick" de cinta al principio (el punto que aparece)
tick = np.sin(2 * np.pi * 2400 * np.arange(int(0.03 * SR)) / SR) * np.exp(-np.arange(int(0.03 * SR)) / SR * 180)
place(stems["fx"], tick, 0.0, 0.3)

# ----------------------------------------------------------------------------
# Mezcla
# ----------------------------------------------------------------------------
# Sidechain: todo lo que no es bombo "respira" con él
side = np.ones(N)
for tt, g in kick_times:
    i = int(tt * SR)
    n = int(BEAT * SR)
    tt_ = np.arange(n) / SR
    duck = 1 - 0.75 * g * np.exp(-tt_ * 11)
    j = min(N, i + n)
    side[i:j] = np.minimum(side[i:j], duck[: j - i])

ir_L = synth_ir(seed=1)
ir_R = synth_ir(seed=2)

dry_mono = (stems["kick"] * 0.95 + stems["clap"] * 0.42 + stems["hats"] * 0.35
            + stems["bass"] * side * 0.6 + stems["fx"] * 0.55)
arp = stems["arp"] * side
bellsig = stems["bell"]

# paneo: arpegio con ping-pong suave, hats ligeramente a la derecha
pp = 0.5 + 0.3 * np.sin(2 * np.pi * t_all / (BEAT * 2))
L = dry_mono + arp * np.cos(pp * np.pi / 2) * 0.55 + bellsig * 0.5 + padL * side
R = dry_mono + arp * np.sin(pp * np.pi / 2) * 0.55 + bellsig * 0.5 + padR * side
R += stems["hats"] * 0.05

send = arp * 0.35 + bellsig * 0.6 + stems["clap"] * 0.25 + (padL + padR) * 0.15 + stems["fx"] * 0.2
L += convolve(send, ir_L) * 0.32
R += convolve(send, ir_R) * 0.32

# bus master: ligera saturación + limitador suave
mix = np.stack([L, R], axis=1)
mix = mix / np.max(np.abs(mix)) * 1.25
mix = np.tanh(mix)
# fade de salida en los últimos 250 ms y de entrada de 5 ms
fade = np.ones(N)
fo = int(0.25 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
fade[: int(0.005 * SR)] = np.linspace(0, 1, int(0.005 * SR))
mix *= fade[:, None]
mix = mix / np.max(np.abs(mix)) * 0.891  # -1 dBFS

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ----------------------------------------------------------------------------
# Análisis por frame para la parte visual
# ----------------------------------------------------------------------------
hop = SR // FPS
nframes = int(DUR * FPS)


def env_track(x, attack=0.0, release=0.12):
    """Envolvente RMS por frame, normalizada, con release suave."""
    vals = []
    for f in range(nframes):
        seg = x[f * hop:(f + 1) * hop]
        vals.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
    v = np.array(vals)
    v /= (v.max() + 1e-9)
    out_ = np.zeros_like(v)
    k = math.exp(-1 / (release * FPS))
    acc = 0.0
    for i, s in enumerate(v):
        acc = s if s > acc else acc * k
        out_[i] = acc
    return np.round(out_, 4).tolist()


mono = mix.mean(axis=1)
win = np.hanning(2048)
bands = 24
edges = np.geomspace(40, 16000, bands + 1)
freqs = np.fft.rfftfreq(2048, 1 / SR)
spec = []
for f in range(nframes):
    c = f * hop + hop // 2
    seg = mono[max(0, c - 1024): c + 1024]
    if len(seg) < 2048:
        seg = np.pad(seg, (0, 2048 - len(seg)))
    mag = np.abs(np.fft.rfft(seg * win))
    row = []
    for b in range(bands):
        m = (freqs >= edges[b]) & (freqs < edges[b + 1])
        row.append(float(np.mean(mag[m])) if m.any() else 0.0)
    spec.append(row)
spec = np.array(spec)
spec = 20 * np.log10(spec + 1e-6)
spec = np.clip((spec - (spec.max() - 60)) / 60, 0, 1)

analysis = dict(
    fps=FPS, bpm=BPM, frames=nframes,
    kick=env_track(stems["kick"], release=0.10),
    clap=env_track(stems["clap"], release=0.10),
    hats=env_track(stems["hats"], release=0.05),
    bass=env_track(stems["bass"], release=0.10),
    bell=env_track(stems["bell"], release=0.25),
    fx=env_track(stems["fx"], release=0.2),
    rms=env_track(mono, release=0.15),
    spectrum=np.round(spec, 3).tolist(),
)
with open(out.rsplit(".", 1)[0] + "_analysis.json", "w") as fh:
    json.dump(analysis, fh)
print("ok", out)
