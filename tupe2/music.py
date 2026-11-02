"""
TUPÉ · "Mirá el verano con otro color" — pieza main de 20 s.
Música compuesta y sintetizada desde cero con numpy (sin samples).

96 BPM · 4/4 · 8 compases = 32 negras = exactamente 20,000 s.
El verano empieza "en gris" también en el audio: mezcla mono y filtrada a ~400 Hz.
Cada vez que aparece color en la imagen, el filtro se abre y la mezcla se abre en estéreo.
La partitura sale como lista de eventos (build/score.json) que maneja la imagen.
"""
import json
import math
import sys
import wave

import numpy as np

from dsp import (SR, rng, midi, place, env_adsr, svf, onepole_hp, polyblep_saw,
                 kick, clap, riser, impact, synth_ir, convolve)

BPM = 96.0
BEAT = 60.0 / BPM          # 0,625 s
BAR = 4 * BEAT             # 2,5 s
DUR = 20.0
N = int(SR * DUR)
t_all = np.arange(N) / SR
bt = lambda b: b * BEAT
EVENTS = []


def ev(kind, b, **kw):
    EVENTS.append(dict(kind=kind, t=round(bt(b), 6), b=b, **kw))


# ----------------------------------------------------------------------------
# Instrumentos
# ----------------------------------------------------------------------------
def steelpan(note, length=1.1, vel=1.0):
    """steel drum: parciales 1 · 2 · 3 (afinados como un pan real) + golpe FM brillante"""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note) * (1 + .012 * np.exp(-t * 40))          # el parche baja de afinación al golpe
    ph = 2 * np.pi * np.cumsum(f) / SR
    idx = 1.4 * vel * np.exp(-t * 30)
    s = np.sin(ph + idx * np.sin(ph * 2)) * np.exp(-t * 3.2)
    s += .45 * np.sin(2 * ph) * np.exp(-t * 5)
    s += .22 * np.sin(2.98 * ph) * np.exp(-t * 9)
    return s * (1 - np.exp(-t * 600)) * .38 * vel


def conga(high=False, slap=False):
    n = int(.35 * SR)
    t = np.arange(n) / SR
    f0 = 330 if high else 215
    f = f0 * (1 + .25 * np.exp(-t * 35))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (16 if slap else 9))
    hit = svf(rng.standard_normal(n), 2500 if slap else 1200, q=1.2, mode="bp") * np.exp(-t * (90 if slap else 140))
    return np.tanh((body + hit * (1.4 if slap else .6)) * 1.3) * .6


def shaker(acc=1.0):
    n = int(.08 * SR)
    t = np.arange(n) / SR
    return onepole_hp(rng.standard_normal(n), 6500) * (1 - np.exp(-t * 300)) * np.exp(-t * 60) * .45 * acc


def bass(note, length):
    n = int((length + .08) * SR)
    t = np.arange(n) / SR
    f = midi(note)
    sub = np.sin(2 * np.pi * f * t)
    body = svf(polyblep_saw(np.full(n, f), n), 160 + 900 * np.exp(-t * 14), q=1.0)
    e = env_adsr(n, .004, .15, .75, .06, length)
    return np.tanh((sub + body * .45) * e * 1.5) * .72


def pad(notes, length, c0, c1):
    n = int((length + .6) * SR)
    L, R = np.zeros(n), np.zeros(n)
    for note in notes:
        f = midi(note)
        for v in range(5):
            d = (v - 2) / 2
            s = polyblep_saw(np.full(n, f * (1 + d * .004)), n, phase0=rng.random())
            pan = .5 + d * .42
            L += s * math.cos(pan * math.pi / 2); R += s * math.sin(pan * math.pi / 2)
    t = np.arange(n) / SR
    cut = c0 * (c1 / c0) ** np.clip(t / length, 0, 1)
    e = env_adsr(n, .12, .4, .8, .5, length)
    g = .045 / len(notes) * 4
    return svf(L, cut, q=.7) * e * g, svf(R, cut, q=.7) * e * g


def whistle(notes):
    """silbido: seno con vibrato que se va abriendo, portamento entre notas y aire filtrado.
    notes = [(negra_inicio, duración_en_negras, midi)]"""
    start, end = bt(notes[0][0]), bt(notes[-1][0] + notes[-1][1])
    n = int((end - start + .25) * SR)
    t = np.arange(n) / SR
    f = np.zeros(n); amp = np.zeros(n)
    for b, d, m in notes:
        i0, i1 = int((bt(b) - start) * SR), int((bt(b + d) - start) * SR)
        f[i0:] = midi(m)
        seg = np.arange(i1 - i0) / SR
        a = np.clip(seg / .03, 0, 1) * np.clip((bt(d) - seg) / .06, 0, 1)
        amp[i0:i1] = np.maximum(amp[i0:i1], a)
    # portamento: suavizo la frecuencia con un polo de ~25 ms
    k = math.exp(-1 / (.025 * SR)); fs = np.empty(n); acc = f[0]
    for i, v in enumerate(f):
        acc = acc * k + v * (1 - k); fs[i] = acc
    vib = 1 + .012 * np.sin(2 * np.pi * 5.6 * t) * np.clip(t / .5, 0, 1)
    ph = 2 * np.pi * np.cumsum(fs * vib) / SR
    tone = np.sin(ph) + .08 * np.sin(2 * ph)
    air = svf(rng.standard_normal(n), fs * 1.0, q=6, mode="bp") * .5
    return (tone + air) * amp * .32, start


def wave_noise(length, up=True):
    """ola: ruido filtrado que sube y rompe"""
    n = int(length * SR)
    t = np.arange(n) / SR
    p = t / length
    cut = 300 * (8000 / 300) ** (p ** 1.4 if up else 1 - p)
    s = svf(rng.standard_normal(n), cut, q=.9)
    return s * (p ** 2 if up else (1 - p) ** 2) * .8


def thump():
    n = int(.4 * SR)
    t = np.arange(n) / SR
    f = 60 + 80 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * .8


def tick():
    n = int(.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200) * .5


def sparkle(base):
    out = np.zeros(int(1.0 * SR))
    for i, nn in enumerate([0, 7, 12, 16, 19, 24]):
        place(out, steelpan(base + nn, .8, .7) * (.6 - i * .07), i * .04)
    return out


# ----------------------------------------------------------------------------
# Partitura
# ----------------------------------------------------------------------------
CH = {
    "Emaj9": dict(root=40, pad=[56, 59, 63, 66], arp=[64, 68, 71, 75, 78]),
    "C#m7": dict(root=37, pad=[56, 59, 64, 68], arp=[61, 64, 68, 71, 76]),
    "Amaj9": dict(root=45, pad=[56, 61, 64, 71], arp=[64, 69, 71, 73, 76]),
    "B6": dict(root=47, pad=[54, 59, 63, 68], arp=[63, 66, 68, 71, 75]),
    "Eadd9": dict(root=40, pad=[56, 59, 64, 66, 71], arp=[64, 66, 68, 71, 76]),
}
HARM = [(0, "Emaj9"), (4, "C#m7"), (8, "Amaj9"), (12, "B6"), (16, "Eadd9"), (20, "C#m7"), (24, "Amaj9"), (28, "Eadd9")]
st = {k: np.zeros(N) for k in ["kick", "perc", "shaker", "bass", "pan", "whistle", "fx", "clap"]}
padL, padR = np.zeros(N), np.zeros(N)

# --- 1 · verano en gris: el sol sube un escalón por negra (latido sordo)
for b in range(4):
    place(st["kick"], thump(), bt(b), .9); ev("sun", b, i=b)
place(st["fx"], tick(), bt(2), .5); ev("label", 2)
place(st["fx"], wave_noise(BEAT * 1.0), bt(3), .6); ev("swell", 3)

# --- groove desde la negra 4
for b in range(4, 32):
    if b in (15,) or b > 28:
        continue
    place(st["kick"], kick(.45), bt(b), .95); ev("kick", b)
for b in [5, 7, 9, 11, 13, 17, 19, 21, 23, 25, 27]:
    place(st["clap"], clap(), bt(b), .55); ev("clap", b)
CONGA = [(0, False, False), (.75, True, False), (1.5, False, True), (2.25, True, False), (2.5, True, True), (3.5, False, False)]
for bar in range(1, 7):
    for off, hi, sl in CONGA:
        b = bar * 4 + off
        if 14.5 <= b < 16:
            continue
        place(st["perc"], conga(hi, sl), bt(b), .8)
        ev("conga", b, hi=hi, slap=sl)
for s in range(16, 112):
    b = s / 4
    if 14.5 <= b < 16:
        continue
    place(st["shaker"], shaker(1 if s % 2 else .5), bt(b), 1)

# --- bajo (negra y contratiempo, saltando la quinta)
for start, name in HARM:
    if start == 0 or start >= 28:
        continue
    r = CH[name]["root"]
    for i, (off, nn, d) in enumerate([(0, r, .35), (.75, r, .2), (1.5, r + 7, .3), (2.5, r + 12, .2), (3, r + 7, .3), (3.5, r, .2)]):
        b = start + off
        if 15 <= b < 16:
            continue
        place(st["bass"], bass(nn, bt(d)), bt(b), 1)
place(st["bass"], bass(28, 2.8), bt(28), 1.1)

# --- pad
for start, name in HARM:
    c0, c1 = (500, 1200) if start < 16 else (1500, 4000)
    if start == 28:
        c0, c1 = 3500, 700
    l, r = pad(CH[name]["pad"], bt(4) if start < 28 else 3.2, c0, c1)
    place(padL, l, bt(start), .9); place(padR, r, bt(start), .9)

# --- steel pan: cada movimiento de los anteojos es una nota
place(st["pan"], steelpan(76, 1.4), bt(4), .9); place(st["pan"], steelpan(71, 1.4), bt(4), .6); ev("glasses", 4, which="caramelo")
for b, nn in [(5, 73), (6, 76), (7, 80)]:
    place(st["pan"], steelpan(nn), bt(b), .8); ev("move", b, midi=nn)
place(st["fx"], wave_noise(BEAT * .5), bt(7.5), .4)
place(st["pan"], steelpan(81, 1.4), bt(8), .9); place(st["pan"], steelpan(76, 1.4), bt(8), .6); ev("swap", 8, to="fluo")
for b, nn in [(9, 78), (10, 76), (11, 73)]:
    place(st["pan"], steelpan(nn), bt(b), .8); ev("move", b, midi=nn)
# carrusel de colores a corcheas
CAROUSEL = ["violeta", "gris", "nude", "caramelo", "fluo", "violeta", "gris", "nude"]
for i, name in enumerate(CAROUSEL):
    b = 12 + i * .5
    nn = [71, 75, 78, 83, 80, 78, 75, 83][i]
    place(st["pan"], steelpan(nn, .7), bt(b), .75)
    ev("swap", b, to=name)
place(st["fx"], riser(BEAT * 2, 300, 9000), bt(14), .65); ev("riser", 14)
for i in range(8):           # redoble de congas
    place(st["perc"], conga(i % 2 == 0, True), bt(14.5 + i * .1875), .35 + .06 * i)

# --- DROP
place(st["fx"], impact(2.8), bt(16), .9); ev("drop", 16)
ev("word", 16, i=0); ev("word", 17, i=1)
place(st["pan"], steelpan(76, 1.6), bt(16), .8); place(st["pan"], steelpan(83, 1.6), bt(17), .8)
for i, name in enumerate(["violeta", "caramelo", "fluo", "gris", "nude"]):
    b = 18 + i * .5
    if b >= 20:
        break
    place(st["pan"], steelpan([80, 83, 85, 88, 92][i], .8), bt(b), .7)
    ev("rain", b, to=name)
WHISTLE_A = [(8, .5, 76), (8.5, .5, 78), (9, 1, 80), (10, .5, 78), (10.5, .5, 76), (11, 1, 73)]
WHISTLE_B = [(16, 1, 80), (17, .5, 83), (17.5, .5, 80), (18, 1, 78), (19, .5, 76), (19.5, .5, 78)]
for phrase in (WHISTLE_A, WHISTLE_B):
    w_, s0 = whistle(phrase); place(st["whistle"], w_, s0, 1)

# --- valor: N° de serie, 21-24 por color
place(st["pan"], steelpan(71, 1.2), bt(20), .7); ev("side", 20)
for i in range(7):
    b = 20.5 + i * .25
    place(st["fx"], tick(), bt(b), .6); ev("count", b, i=i)
place(st["pan"], steelpan(83, 1.4), bt(22), .85); ev("count_land", 22)
place(st["pan"], steelpan(78, 1.2), bt(23), .7); ev("made", 23)

# --- único: cinco pares, uno queda en color
for i in range(5):
    b = 24 + i * .5
    place(st["pan"], steelpan([64, 68, 71, 75, 78][i], .8), bt(b), .65); ev("grid", b, i=i)
place(st["fx"], thump(), bt(26), .7); place(st["pan"], steelpan(80, 1.6), bt(26), .8); ev("choose", 26)
ev("line", 26, i=0); ev("line", 27, i=1)
place(st["fx"], tick(), bt(27.5), .7); ev("stamp", 27.5)

# --- cierre
place(st["fx"], impact(2.2), bt(28), .7); ev("final", 28)
place(st["pan"], steelpan(76, 2.6), bt(28), .7); place(st["pan"], steelpan(83, 2.6), bt(28), .45)
for i in range(8):
    ev("piece", 28 + i * .125, i=i)
place(st["pan"], steelpan(80, 1.2), bt(29), .6); ev("cta", 29, i=0)
place(st["pan"], steelpan(83, 1.2), bt(30), .6); ev("cta", 30, i=1)
place(st["whistle"], sparkle(76), bt(31), .55); ev("sparkle", 31)

# ----------------------------------------------------------------------------
# Mezcla: el "color" del sonido
# ----------------------------------------------------------------------------
def color_amt(b):
    if b < 4: return 0.0
    if b < 8: return .55
    if b < 12: return .72
    if b < 16: return .72 + .2 * (b - 12) / 4
    return 1.0


amt = np.array([color_amt(b) for b in t_all / BEAT])
k = math.exp(-1 / (.05 * SR)); sm = np.empty(N); a = 0.0
for i, v in enumerate(amt):          # 50 ms de deslizamiento para que la apertura no haga clic
    a = a * k + v * (1 - k); sm[i] = a
amt = sm

side = np.ones(N)
for e in EVENTS:
    if e["kind"] in ("kick", "drop", "final"):
        i = int(e["t"] * SR); n = int(BEAT * SR); tt = np.arange(n) / SR
        j = min(N, i + n); side[i:j] = np.minimum(side[i:j], (1 - .55 * np.exp(-tt * 9))[: j - i])

mono = (st["kick"] * .9 + st["clap"] * .35 + st["perc"] * .5 + st["shaker"] * .3 + st["bass"] * side * .6 + st["fx"] * .5)
pan_ = st["pan"] * (.8 + .2 * side)
pp = .5 + .25 * np.sin(2 * np.pi * t_all / (BEAT * 2))
L = mono + pan_ * np.cos(pp * np.pi / 2) * .7 + st["whistle"] * .5 + padL * side
R = mono + pan_ * np.sin(pp * np.pi / 2) * .7 + st["whistle"] * .5 + padR * side
R = R + st["perc"] * .08
send = pan_ * .4 + st["whistle"] * .5 + st["clap"] * .25 + (padL + padR) * .1 + st["fx"] * .15
L += convolve(send, synth_ir(2.4, 2.4, seed=5)) * .3
R += convolve(send, synth_ir(2.4, 2.4, seed=6)) * .3

# ancho estéreo y brillo siguen al color
M, S = (L + R) / 2, (L - R) / 2
S *= amt
L, R = M + S, M - S
cut = 380 * (20000 / 380) ** amt
L = svf(L, cut, q=.75)
R = svf(R, cut, q=.75)

mix = np.stack([L, R], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.15)
fade = np.ones(N); fo = int(.4 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
fade[: int(.004 * SR)] = np.linspace(0, 1, int(.004 * SR))
mix *= fade[:, None]
mix = mix / np.max(np.abs(mix)) * .84          # −1,5 dBFS (margen para el AAC)

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
EVENTS.sort(key=lambda e: e["t"])
json.dump(dict(bpm=BPM, beat=BEAT, bar=BAR, dur=DUR, events=EVENTS),
          open(out.rsplit("/", 1)[0] + "/score.json", "w"), indent=0)
print("ok", out, len(EVENTS), "eventos")
