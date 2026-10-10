"""
Música del spot TUPÉ · Carla Di Sí — compuesta y sintetizada desde cero (numpy, sin samples).

112 BPM · 4/4 · 7 compases = 28 negras = exactamente 15,000 s.
La partitura es una lista de EVENTOS con nombre. El mismo archivo de eventos
(build/score.json) maneja la imagen: cada golpe que suena es un golpe que se ve.
"""
import json
import math
import sys
import wave

import numpy as np

from dsp import (SR, rng, midi, place, env_adsr, svf, onepole_hp, polyblep_saw,
                 kick, clap, riser, impact, synth_ir, convolve)

BPM = 112.0
BEAT = 60.0 / BPM          # 0,5357 s
BAR = 4 * BEAT             # 2,1429 s
DUR = 15.0
N = int(SR * DUR)
t_all = np.arange(N) / SR


def bt(b):
    """tiempo (s) de la negra b (puede ser fraccionaria)"""
    return b * BEAT


EVENTS = []


def ev(kind, b, **kw):
    EVENTS.append(dict(kind=kind, t=round(bt(b), 6), b=b, **kw))


# ----------------------------------------------------------------------------
# Instrumentos propios de esta pieza
# ----------------------------------------------------------------------------

def marimba(note, length=0.9, bright=1.0):
    """Marimba FM: portadora 1 : moduladora 4, índice que cae muy rápido (golpe de maza)."""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note)
    idx = (2.6 * bright) * np.exp(-t * 38) + 0.15
    mod = np.sin(2 * np.pi * f * 4.0 * t) * idx
    body = np.sin(2 * np.pi * f * t + mod)
    # resonador del tubo: el 4º armónico suena un instante
    tube = np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 60) * 0.18
    return (body * np.exp(-t * 5.5) + tube) * 0.5


def bell(note, length=2.4):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note)
    idx = 1.8 * np.exp(-t * 4) + 0.2
    mod = np.sin(2 * np.pi * f * 3.5 * t) * idx
    s = np.sin(2 * np.pi * f * t + mod) + 0.3 * np.sin(2 * np.pi * f * 2 * t + mod * .4)
    return s * np.exp(-t * 2.2) * 0.32


def bloop(f0, f1, length=0.28):
    """gota/burbuja: seno con glissando exponencial (el 'pop' de un disco que aparece)"""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** np.clip(t / 0.09, 0, 1)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * np.exp(-t * 16) * (1 - np.exp(-t * 900)) * 0.8


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    s = svf(rng.standard_normal(n), 3200, q=2.2, mode="bp") * np.exp(-t * 60)
    s += np.sin(2 * np.pi * 880 * t * (1 + 2 * np.exp(-t * 80))) * np.exp(-t * 35) * .4
    return s


def shaker(accent=1.0):
    n = int(0.07 * SR)
    t = np.arange(n) / SR
    x = onepole_hp(rng.standard_normal(n), 6000)
    e = (1 - np.exp(-t * 400)) * np.exp(-t * 70)
    return x * e * 0.5 * accent


def whoosh(length, up=True):
    n = int(length * SR)
    t = np.arange(n) / SR
    p = t / length
    cut = 400 * (7000 / 400) ** (p if up else 1 - p)
    s = svf(rng.standard_normal(n), cut, q=1.4, mode="bp")
    env = np.sin(np.pi * np.clip(p, 0, 1)) ** 1.5 if up else (1 - p) ** 2
    return s * env * 0.9


def bass(note, length):
    n = int((length + 0.06) * SR)
    t = np.arange(n) / SR
    f = midi(note)
    sub = np.sin(2 * np.pi * f * t)
    body = svf(polyblep_saw(np.full(n, f), n), 180 + 1400 * np.exp(-t * 18), q=1.2)
    e = env_adsr(n, 0.003, 0.12, 0.7, 0.05, length)
    return np.tanh((sub * 0.9 + body * 0.5) * e * 1.4) * 0.75


def pad(notes, length, cut0, cut1):
    n = int((length + 0.5) * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    for note in notes:
        f = midi(note)
        for v in range(5):
            d = (v - 2) / 2
            s = polyblep_saw(np.full(n, f * (1 + d * 0.0045)), n, phase0=rng.random())
            pan = 0.5 + d * 0.4
            L += s * math.cos(pan * math.pi / 2)
            R += s * math.sin(pan * math.pi / 2)
    t = np.arange(n) / SR
    cut = cut0 * (cut1 / cut0) ** np.clip(t / length, 0, 1)
    e = env_adsr(n, 0.08, 0.4, 0.8, 0.45, length)
    g = 0.05 / len(notes) * 4
    return svf(L, cut, q=0.8) * e * g, svf(R, cut, q=0.8) * e * g


def sparkle(base):
    """arpegio brillante y corto (destello sobre el acento de la É)"""
    out = np.zeros(int(0.9 * SR))
    for i, nn in enumerate([0, 7, 12, 16, 19, 24]):
        s = bell(base + nn, 0.8) * (0.55 - i * 0.06)
        place(out, s, i * 0.035)
    return out


# ----------------------------------------------------------------------------
# Partitura (en negras; 0..28)
# ----------------------------------------------------------------------------
CH = {
    "F#m9": dict(root=42, pad=[57, 61, 64, 68]),
    "Dmaj9": dict(root=38, pad=[57, 61, 64, 66]),
    "E6": dict(root=40, pad=[56, 59, 61, 64]),
    "C#m7": dict(root=37, pad=[56, 59, 64, 68]),
    "Aadd9": dict(root=45, pad=[57, 61, 64, 71]),
}
# acorde por negra de inicio y duración en negras
HARM = [(0, 4, "F#m9"), (4, 4, "Dmaj9"), (8, 4, "E6"), (12, 4, "C#m7"),
        (16, 4, "Aadd9"), (20, 2, "F#m9"), (22, 2, "Dmaj9"), (24, 4, "Aadd9")]

st = {k: np.zeros(N) for k in ["kick", "clap", "shaker", "bass", "mallet", "fx", "bell"]}
padL, padR = np.zeros(N), np.zeros(N)

# --- compás 1 (0-4): dos discos aparecen, la montura se dibuja y se llena
place(st["fx"], bloop(140, 330), bt(0), 0.9); ev("disc", 0, which=0)
place(st["kick"], kick(0.45, 0.6), bt(0), 0.55)
place(st["fx"], bloop(190, 470), bt(1), 0.9); ev("disc", 1, which=1)
place(st["kick"], kick(0.45, 0.6), bt(1), 0.55)
place(st["fx"], whoosh(BEAT * 1.0), bt(2), 0.55); ev("draw", 2)
place(st["kick"], kick(0.45, 0.6), bt(2), 0.4)
place(st["clap"], clap(), bt(3), 0.8); place(st["fx"], pop(), bt(3), 0.7); ev("fill", 3)

# --- groove: bombo en negras (con hueco antes del drop), palmas en 2 y 4
KICKS = [b for b in range(4, 28) if b not in (15,) and b < 25] + [24]
KICKS = sorted(set(KICKS))
for b in KICKS:
    place(st["kick"], kick(), bt(b), 1.0); ev("kick", b)
for b in [5, 7, 9, 11, 13, 17, 19, 21, 23]:
    place(st["clap"], clap(), bt(b), 0.75); ev("clap", b)
# redoble de palmas al final del compás 3 (cambio de color en corcheas)
for b in [11.5]:
    place(st["clap"], clap(), bt(b), 0.45); ev("clap", b)
for s in range(4 * 4, 24 * 4):           # semicorcheas desde la negra 4 a la 24
    b = s / 4
    if 14.5 <= b < 16 or b < 4:
        continue
    acc = 1.0 if s % 2 == 1 else 0.45
    place(st["shaker"], shaker(acc), bt(b), 1.0)
    if s % 2 == 1:
        ev("shake", b)

# --- bajo a contratiempo
for start, dur, name in HARM:
    if start < 4:
        continue
    for b in range(start, start + dur):
        if b in (15,) or b >= 24:
            continue
        place(st["bass"], bass(CH[name]["root"], BEAT * 0.42), bt(b + 0.5), 1.0)
place(st["bass"], bass(33, 2.4), bt(24), 1.0)

# --- pad
for start, dur, name in HARM:
    c0, c1 = (300, 1500) if start == 0 else ((900, 2600) if start < 16 else (1800, 4200))
    if start == 24:
        c0, c1 = 3500, 900
    l, r = pad(CH[name]["pad"], bt(dur) if start < 24 else 2.2, c0, c1)
    place(padL, l, bt(start), 0.9)
    place(padR, r, bt(start), 0.9)

# --- marimba: arpegio sincopado en los compases 2-3 (cada nota es un evento "note")
ARP = {"Dmaj9": [62, 66, 69, 73, 76], "E6": [64, 68, 71, 73, 76]}
pattern = [0, 2, 4, 2, 3, 1, 4, 2]          # corcheas
rhythm = [0, 0.5, 1.0, 1.75, 2.0, 2.5, 3.0, 3.5]
for bar_start, name in [(4, "Dmaj9"), (8, "E6")]:
    for i, off in enumerate(rhythm):
        if bar_start == 8 and off >= 3.0:
            continue
        nn = ARP[name][pattern[i]]
        place(st["mallet"], marimba(nn), bt(bar_start + off), 0.75)
        ev("note", bar_start + off, midi=nn)
# cambios de color a corcheas en la negra 11 → cuatro golpes de marimba
for i, off in enumerate([11.0, 11.25, 11.5, 11.75]):
    nn = [76, 73, 71, 68][i]
    place(st["mallet"], marimba(nn, 0.5), bt(off), 0.7); ev("note", off, midi=nn)

# --- compás 4 (12-16): producto en 3D; cada etiqueta = una nota
for b, nn, label in [(12, 61, "turn"), (13, 68, "c1"), (14, 71, "c2"), (14.5, 73, "c3")]:
    place(st["mallet"], marimba(nn, 1.2, 0.8), bt(b), 0.8)
    ev("callout", b, id=label, midi=nn)
place(st["fx"], riser(BEAT * 2.0, 300, 10000), bt(14), 0.7); ev("riser", 14)

# --- compás 5 (16-20): DROP. El logo TUPÉ se arma pieza por pieza en corcheas
place(st["fx"], impact(2.5), bt(16), 0.85); ev("impact", 16)
LOGO_NOTES = [57, 61, 64, 66, 69, 73, 76, 81]
for i, nn in enumerate(LOGO_NOTES):
    b = 16 + i * 0.5
    place(st["mallet"], marimba(nn, 0.9, 1.0), bt(b), 0.85)
    ev("piece", b, i=i, midi=nn)
place(st["bell"], sparkle(69), bt(19.5), 0.7); ev("sparkle", 19.5)

# --- compás 6 (20-24): key visual + firma escrita a mano
place(st["fx"], whoosh(BEAT * 0.9, up=True), bt(19.55), 0.6); ev("whip", 20)
ev("slide", 20, which=0); ev("slide", 21, which=1)
SIGN = [(21.0, 69), (21.5, 73), (22.0, 76), (22.25, 78), (22.5, 76), (23.0, 73), (23.25, 76), (23.5, 81)]
for b, nn in SIGN:
    place(st["mallet"], marimba(nn, 0.8, 0.7), bt(b), 0.7)
    ev("stroke", b, midi=nn)

# --- compás 7 (24-28): cierre
place(st["fx"], whoosh(BEAT * 0.7, up=True), bt(23.35), 0.5)
place(st["fx"], impact(2.0), bt(24), 0.7); ev("final", 24)
place(st["bell"], bell(69, 3.0), bt(24), 0.7)
place(st["bell"], bell(76, 3.0), bt(24), 0.45)
for i, b in enumerate([25, 26]):
    place(st["mallet"], marimba([73, 76][i], 1.0, 0.6), bt(b), 0.6)
    ev("line", b, i=i)
place(st["bell"], sparkle(69), bt(27), 0.55); ev("sparkle", 27)

# ----------------------------------------------------------------------------
# Mezcla
# ----------------------------------------------------------------------------
side = np.ones(N)
for e in EVENTS:
    if e["kind"] in ("kick", "impact", "final"):
        i = int(e["t"] * SR)
        n = int(BEAT * SR)
        tt = np.arange(n) / SR
        duck = 1 - 0.6 * np.exp(-tt * 10)
        j = min(N, i + n)
        side[i:j] = np.minimum(side[i:j], duck[: j - i])

dry = (st["kick"] * 0.9 + st["clap"] * 0.38 + st["shaker"] * 0.32
       + st["bass"] * side * 0.55 + st["fx"] * 0.5)
mallet = st["mallet"] * (0.75 + 0.25 * side)
pp = 0.5 + 0.22 * np.sin(2 * np.pi * t_all / (BEAT * 4))
L = dry + mallet * np.cos(pp * np.pi / 2) * 0.62 + st["bell"] * 0.45 + padL * side
R = dry + mallet * np.sin(pp * np.pi / 2) * 0.62 + st["bell"] * 0.45 + padR * side
R += st["shaker"] * 0.06

send = mallet * 0.45 + st["bell"] * 0.6 + st["clap"] * 0.3 + (padL + padR) * 0.12 + st["fx"] * 0.15
L += convolve(send, synth_ir(2.2, 2.6, seed=3)) * 0.3
R += convolve(send, synth_ir(2.2, 2.6, seed=4)) * 0.3

mix = np.stack([L, R], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.2)
fade = np.ones(N)
fo = int(0.35 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
fade[: int(0.004 * SR)] = np.linspace(0, 1, int(0.004 * SR))
mix *= fade[:, None]
mix = mix / np.max(np.abs(mix)) * 0.891   # −1 dBFS

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

EVENTS.sort(key=lambda e: e["t"])
with open(out.rsplit("/", 1)[0] + "/score.json" if "/" in out else "score.json", "w") as fh:
    json.dump(dict(bpm=BPM, beat=BEAT, bar=BAR, events=EVENTS), fh, indent=0)
print("ok", out, len(EVENTS), "eventos")
