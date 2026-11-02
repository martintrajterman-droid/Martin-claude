"""
TUPÉ · "Mirá el verano con otro color" — versión FÁBRICA (20 s).
Techno ácido que nace de la máquina, sintetizado desde cero con numpy: los motores paso
a paso de la cortadora láser "cantan" (su zumbido tiene altura y acá toca la melodía), el
láser, las mordazas, los tubos fluorescentes y el tambor de pulido son la percusión.

144 BPM · 12 compases = 48 negras = exactamente 20,000 s.
"""
import json
import math
import sys
import wave

import numpy as np

from dsp import SR, rng, midi, place, env_adsr, svf, onepole_hp, polyblep_saw, kick, clap, riser, impact, synth_ir, convolve

BPM = 144.0
BEAT = 60 / BPM
DUR = 20.0
N = int(SR * DUR)
t_all = np.arange(N) / SR
bt = lambda b: b * BEAT
EVENTS = []


def ev(kind, b, **kw):
    EVENTS.append(dict(kind=kind, t=round(bt(b), 6), b=b, **kw))


# ----------------------------------------------------------------------------
# Sonidos de fábrica
# ----------------------------------------------------------------------------
def stepper(note, length):
    """motor paso a paso: cuadrada con 'micro-pasos' (zumbido con altura) + resonancia de chasis"""
    n = int(length * SR); t = np.arange(n) / SR; f = midi(note)
    sq = np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sign(np.sin(2 * np.pi * f * 2 * t)) * .2
    chat = (np.sin(2 * np.pi * f / 4 * t) > .7) * .3
    s = svf(sq + chat, 2400, q=1.5) + svf(rng.standard_normal(n), f * 3, q=4, mode="bp") * .15
    return s * env_adsr(n, .005, .02, .9, .02, length) * .25


def laser_zap(length=.05):
    n = int(length * SR); t = np.arange(n) / SR
    return (svf(rng.standard_normal(n), 7000, q=1.2, mode="bp") + np.sin(2 * np.pi * 3100 * t) * .4) * np.exp(-t * 60) * .5


def laser_hum(length):
    n = int(length * SR); t = np.arange(n) / SR
    s = polyblep_saw(np.full(n, 1180 * (1 + .01 * np.sin(2 * np.pi * 7 * t))), n) * .2
    crackle = svf(rng.standard_normal(n) * (rng.random(n) < .02), 5000, q=1, mode="bp") * 2
    return (svf(s, 3000, q=1) + crackle) * np.clip(t / .02, 0, 1) * np.clip((length - t) / .03, 0, 1) * .3


def clank():
    n = int(.4 * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in [(312, 14), (847, 22), (1493, 30), (2210, 40)])
    hit = svf(rng.standard_normal(n), 2500, q=1, mode="bp") * np.exp(-t * 90)
    return (s * .25 + hit * .8) * .7


def lights_on():
    """tubos fluorescentes: zumbido de 100 Hz con parpadeos (clics del arrancador)"""
    n = int(1.0 * SR); t = np.arange(n) / SR
    hum = (np.sin(2 * np.pi * 100 * t) + .4 * np.sin(2 * np.pi * 200 * t)) * .15
    flick = np.zeros(n)
    for c in [.0, .08, .13, .3]:
        i = int(c * SR); flick[i:i + 400] += rng.standard_normal(400) * .6 * np.exp(-np.arange(400) / 60)
    return hum * np.clip(t / .3, 0, 1) * np.exp(-t * 1.5) + flick


def tumbler(length):
    """tambor de pulido: piezas que ruedan (granos de ruido con ritmo de rotación)"""
    n = int(length * SR); t = np.arange(n) / SR
    g = rng.standard_normal(n) * (rng.random(n) < .006)
    g = svf(g, 3200, q=2, mode="bp") * 3
    roll = .5 + .5 * np.sin(2 * np.pi * (BPM / 60) * t) ** 2
    return g * roll * .35


def whoosh(length):
    n = int(length * SR); t = np.arange(n) / SR; p = t / length
    return svf(rng.standard_normal(n), 400 * (6000 / 400) ** p, q=1.2, mode="bp") * np.sin(np.pi * p) ** 1.4 * .7


# ----------------------------------------------------------------------------
# Banda
# ----------------------------------------------------------------------------
def acid(note, length, accent=False, slide_to=None):
    """línea ácida tipo 303: sierra con filtro resonante y envolvente, acentos y ligados"""
    n = int(length * SR); t = np.arange(n) / SR
    f0 = midi(note)
    f = np.full(n, f0) if slide_to is None else f0 * (midi(slide_to) / f0) ** np.clip(t / (length * .6), 0, 1)
    s = polyblep_saw(f, n)
    cut = 300 + (2600 if accent else 1400) * np.exp(-t * (9 if accent else 14))
    y = svf(s, cut, q=6 if accent else 4)
    return np.tanh(y * 2.2) * env_adsr(n, .003, .05, .7, .02, length) * .35


def hat(open_=False):
    n = int((.15 if open_ else .035) * SR); t = np.arange(n) / SR
    return onepole_hp(rng.standard_normal(n), 8500) * np.exp(-t * (20 if open_ else 120)) * .45


def pad(notes, length):
    n = int((length + .5) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for note in notes:
        for d in (-.004, 0, .004):
            s += polyblep_saw(np.full(n, midi(note) * (1 + d)), n, phase0=rng.random())
    return svf(s, 1800, q=.7) * env_adsr(n, .3, .4, .8, .5, length) * .04 / len(notes) * 3


def sparkle(base):
    out = np.zeros(int(1.0 * SR))
    for i, nn in enumerate([0, 7, 12, 16, 19, 24]):
        n = int(.6 * SR); t = np.arange(n) / SR; f = midi(base + nn)
        place(out, np.sin(2 * np.pi * f * t + np.exp(-t * 20) * np.sin(2 * np.pi * f * 3 * t)) * np.exp(-t * 5) * (.4 - i * .05), i * .04)
    return out


st = {k: np.zeros(N) for k in ["mach", "kick", "clap", "hats", "acid", "pad", "fx", "step"]}

# --- encendido
place(st["mach"], lights_on(), bt(1.4), 1); ev("lights", 2)
place(st["mach"], whoosh(bt(1)), bt(2), .6); ev("sheet", 3, i=0)
place(st["mach"], clank(), bt(3.5), .9); ev("clamp", 3.5)
place(st["mach"], clank(), bt(4), .9); ev("clamp", 4)
# --- grabado láser (raster): zaps en semicorcheas
for s in range(16, 32):
    b = s / 4
    place(st["fx"], laser_zap(), bt(b), .5 if s % 2 else .8)
ev("engrave", 4, line=0, end=6); ev("engrave", 6, line=1, end=8)
# --- corte del primer frente: los motores tocan la melodía
place(st["fx"], laser_hum(bt(6)), bt(8), 1)
MELODY = [65, 68, 72, 70, 68, 65, 63, 65, 68, 72, 75, 72]
for i, nn in enumerate(MELODY):
    b = 8 + i * .5
    place(st["step"], stepper(nn, bt(.48)), bt(b), 1); ev("step", b, midi=nn)
ev("cut", 8, i=0, end=14)
place(st["fx"], laser_zap(.12), bt(14), 1); ev("flood", 14, i=0)
place(st["mach"], whoosh(bt(1)), bt(14.6), .5); ev("lift", 15, i=0)
# --- carrusel: cuatro planchas más, una cada dos negras
for k, (b, name) in enumerate([(16, "fluo"), (18, "violeta"), (20, "gris"), (22, "nude")]):
    place(st["mach"], clank(), bt(b), .7); ev("sheet", b, i=k + 1)
    place(st["fx"], laser_hum(bt(.9)), bt(b + .1), 1)
    for j in range(4):
        place(st["step"], stepper([72, 75, 77, 80][j] - (k % 2) * 3, bt(.24)), bt(b + .1 + j * .22), .9)
    ev("cut", b + .1, i=k + 1, end=b + 1)
    place(st["fx"], laser_zap(.1), bt(b + 1), 1); ev("flood", b + 1, i=k + 1)
    ev("lift", b + 1.5, i=k + 1)
ev("word", 16, i=0); ev("word", 18, i=1)
place(st["fx"], riser(bt(4), 300, 9000), bt(20), .6); ev("riser", 20)

# --- ritmo de máquina desde la negra 8 (bombo), palmas medio tiempo, hats desde 16
for b in range(8, 46):
    if 23 <= b < 24:
        continue
    place(st["kick"], kick(.35), bt(b), .55 if b < 24 else .95); ev("kick", b)
for b in range(10, 46, 4):
    if 23 <= b < 24: continue
    place(st["clap"], clap(), bt(b), .55); ev("clap", b)
for s in range(32, 184):
    b = s / 4
    if 23 <= b < 24 or b >= 46: continue
    if b < 24 and s % 2 == 0: continue
    place(st["hats"], hat(s % 4 == 2), bt(b), .5 if s % 4 == 2 else .3)

# --- DROP: tambor de pulido + ácido + pad
place(st["fx"], impact(2.4), bt(24), .9); ev("drop", 24)
ev("word2", 24, i=0); ev("word2", 25, i=1)
place(st["mach"], tumbler(bt(8)), bt(24), 1)
ACID = [(0, 41, 1, None), (.5, 41, 0, None), (.75, 53, 1, None), (1, 41, 0, None), (1.5, 44, 0, 41), (2, 41, 1, None), (2.5, 48, 0, None),
        (2.75, 41, 0, None), (3, 51, 1, None), (3.5, 41, 0, 46)]
for bar in range(6, 12):
    for off, nn, acc, sl in ACID:
        b = bar * 4 + off
        if b >= 46: continue
        place(st["acid"], acid(nn, bt(.45), bool(acc), sl), bt(b), 1)
for bar, notes in [(6, [53, 56, 60, 63]), (7, [49, 53, 56, 60]), (8, [51, 55, 58, 62]), (9, [53, 56, 60, 63]), (10, [49, 53, 56, 60]), (11, [53, 56, 60, 65])]:
    place(st["pad"], pad(notes, bt(4)), bt(bar * 4), 1)
for i in range(8):
    ev("spin", 24 + i, i=i)

# --- grabado del número de serie en la patilla
place(st["fx"], laser_hum(bt(2)), bt(32), .8)
for s in range(128, 136):
    place(st["fx"], laser_zap(), bt(s / 4), .6)
ev("serial", 32, end=34)
for i, b in enumerate([35, 36, 37]):
    place(st["mach"], clank(), bt(b), .35); ev("vline", b, i=i)
ev("yline", 38, i=0); ev("yline", 39, i=1)

# --- cierre: el láser recorta el logo
place(st["fx"], impact(2.0), bt(40), .6); ev("final", 40)
place(st["fx"], laser_hum(bt(2)), bt(40), .9)
for i in range(8):
    b = 40 + i * .25
    place(st["fx"], laser_zap(), bt(b), .8); ev("piece", b, i=i)
ev("cta", 42, i=0); ev("cta", 43, i=1)
ev("store", 44); ev("sign", 44.5)
place(st["fx"], sparkle(77), bt(47), .7); ev("sparkle", 47)

# ----------------------------------------------------------------------------
# Mezcla
# ----------------------------------------------------------------------------
side = np.ones(N)
for e in EVENTS:
    if e["kind"] == "kick" and e["b"] >= 24:
        i = int(e["t"] * SR); n = int(BEAT * SR); tt = np.arange(n) / SR
        j = min(N, i + n); side[i:j] = np.minimum(side[i:j], (1 - .5 * np.exp(-tt * 12))[: j - i])
dry = st["kick"] * .9 + st["clap"] * .45 + st["hats"] * .3 + st["acid"] * side * .8 + st["fx"] * .45 + st["mach"] * .6 + st["step"] * .8
pp = .5 + .3 * np.sin(2 * np.pi * t_all / (BEAT * 4))
L = dry + st["pad"] * side * np.cos(pp * np.pi / 2) * 1.3 + st["hats"] * .05
R = dry + st["pad"] * side * np.sin(pp * np.pi / 2) * 1.3
send = st["clap"] * .3 + st["step"] * .25 + st["pad"] * .4 + st["acid"] * .1
L += convolve(send, synth_ir(1.4, 3.6, seed=12)) * .3
R += convolve(send, synth_ir(1.4, 3.6, seed=13)) * .3
mix = np.stack([L, R], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.2)
fade = np.ones(N); fo = int(.4 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
fade[: int(.004 * SR)] = np.linspace(0, 1, int(.004 * SR))
mix *= fade[:, None]
mix = mix / np.max(np.abs(mix)) * .84
out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
EVENTS.sort(key=lambda e: e["t"])
json.dump(dict(bpm=BPM, beat=BEAT, dur=DUR, events=EVENTS), open(out.rsplit("/", 1)[0] + "/score.json", "w"), indent=0)
print("ok", out, len(EVENTS), "eventos")
