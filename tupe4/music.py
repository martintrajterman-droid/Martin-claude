"""
TUPÉ · "Mirá el verano con otro color" — versión CIUDAD (20 s).
Cumbia digital porteña compuesta y sintetizada desde cero con numpy: güira, cencerro,
timbal, bajo, acordeón de lengüetas sintetizado y "pews". La calle también es síntesis
(tránsito, colectivo, bocina). Sin samples.

108 BPM · 9 compases = 36 negras = exactamente 20,000 s.
Gesto sonoro: la cumbia empieza lejos (como desde la ventana de un vecino, filtrada y baja)
y cada piso que sube la cámara la acerca un escalón; en la terraza suena entera.
"""
import json
import math
import sys
import wave

import numpy as np

from dsp import SR, rng, midi, place, env_adsr, svf, onepole_hp, kick, riser, impact, synth_ir, convolve

BPM = 108.0
BEAT = 60 / BPM
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
def guira(long=False):
    """güira: raspado metálico = ráfaga de ruido modulada por los dientes del rallador"""
    n = int((.14 if long else .05) * SR); t = np.arange(n) / SR
    teeth = .6 + .4 * np.sign(np.sin(2 * np.pi * (180 if long else 260) * t))
    x = onepole_hp(rng.standard_normal(n), 5500) * teeth
    e = (1 - np.exp(-t * 300)) * np.exp(-t * (18 if long else 70))
    return x * e * .45


def cowbell():
    """cencerro estilo 808: dos cuadradas inarmónicas filtradas"""
    n = int(.25 * SR); t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 540 * t)) + np.sign(np.sin(2 * np.pi * 800 * t))
    s = svf(s, 2600, q=2.5, mode="bp")
    return s * np.exp(-t * 14) * .35


def timbal(f=420, rim=False):
    n = int(.3 * SR); t = np.arange(n) / SR
    ff = f * (1 + .15 * np.exp(-t * 40))
    body = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * (30 if rim else 9))
    ring = np.sin(2 * np.pi * f * 1.6 * t) * np.exp(-t * 14) * .25
    stick = svf(rng.standard_normal(n), 3500, q=1.5, mode="bp") * np.exp(-t * 120)
    return np.tanh((body + ring + stick * (1.6 if rim else .7)) * 1.2) * .5


def bass(note, length):
    n = int((length + .06) * SR); t = np.arange(n) / SR
    f = midi(note)
    s = np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8)
    e = env_adsr(n, .005, .1, .7, .05, length)
    return np.tanh(s * e * 1.6) * .7


def accordion(notes, length, vib=True):
    """acordeón: dos lengüetas por nota (una desafinada +6 cents = el 'musette'),
    pulsos estrechos, fuelle con ataque lento y trémolo natural del batido"""
    n = int((length + .1) * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for note in notes:
        f = midi(note)
        for det, amp in [(1, 1), (1.0035, .8), (2, .25)]:
            ph = (f * det * t + (.003 * np.sin(2 * np.pi * 5.5 * t) if vib else 0)) % 1.0
            pulse = np.where(ph < .32, 1.0, -.47)
            s += pulse * amp
    s = svf(s, 2600, q=.8)
    e = env_adsr(n, .03, .08, .85, .07, length) * (1 + .06 * np.sin(2 * np.pi * 6 * t))
    return s * e * .09 / len(notes) * 2


def pew(f0=1800, f1=200, length=.22):
    n = int(length * SR); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / length)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * .35


def traffic(length):
    """rumor de ciudad: ruido marrón filtrado + motor lejano"""
    n = int(length * SR); t = np.arange(n) / SR
    br = np.cumsum(rng.standard_normal(n)); br = br - np.convolve(br, np.ones(4800) / 4800, "same")
    br = br / np.max(np.abs(br))
    hum = np.sin(2 * np.pi * 48 * t + 2 * np.sin(2 * np.pi * .3 * t)) * .3
    return (svf(br, 500, q=.6) * .8 + hum * .4) * .5


def colectivo(length=1.6):
    """colectivo que pasa: motor diésel (sierra grave con golpeteo) + efecto Doppler y paneo"""
    n = int(length * SR); t = np.arange(n) / SR; p = t / length
    f = 52 * (1 + .06 * np.tanh((.5 - p) * 6))           # Doppler
    ph = 2 * np.pi * np.cumsum(f) / SR
    eng = (np.sin(ph) + .5 * np.sin(2 * ph) + .3 * np.sign(np.sin(ph * 4)))
    eng *= (1 + .3 * np.sin(ph / 2))
    air = svf(rng.standard_normal(n), 800 + 1500 * np.sin(np.pi * p), q=.7)
    env = np.sin(np.pi * p) ** 2
    return svf(eng, 900, q=.7) * env * .5 + air * env * .3, p


def bocina():
    n = int(.32 * SR); t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 415 * t)) + np.sign(np.sin(2 * np.pi * 523 * t))
    return svf(s, 1800, q=1) * np.clip(t / .01, 0, 1) * np.clip((.32 - t) / .03, 0, 1) * .25


def whoosh(length, up=True):
    n = int(length * SR); t = np.arange(n) / SR; p = t / length
    cut = 400 * (6000 / 400) ** (p if up else 1 - p)
    return svf(rng.standard_normal(n), cut, q=1.3, mode="bp") * np.sin(np.pi * p) ** 1.5 * .8


def thump():
    n = int(.4 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(60 + 70 * np.exp(-t * 25)) / SR) * np.exp(-t * 9) * .8


def sparkle(base):
    out = np.zeros(int(1.0 * SR))
    for i, nn in enumerate([0, 7, 12, 16, 19, 24]):
        n = int(.6 * SR); t = np.arange(n) / SR; f = midi(base + nn)
        s = np.sin(2 * np.pi * f * t + 1.2 * np.exp(-t * 20) * np.sin(2 * np.pi * f * 3 * t)) * np.exp(-t * 5)
        place(out, s * (.4 - i * .05), i * .04)
    return out


# ----------------------------------------------------------------------------
# Partitura: La menor, cadencia andaluza (Am · G · F · E), como manda la cumbia
# ----------------------------------------------------------------------------
CH = {"Am": (45, [57, 60, 64]), "G": (43, [55, 59, 62]), "F": (41, [53, 57, 60]), "E": (40, [56, 59, 64]), "C": (48, [55, 60, 64])}
HARM = ["Am", "Am", "G", "F", "E", "Am", "G", "F", "Am"]
st = {k: np.zeros(N) for k in ["kick", "perc", "bass", "acc", "fx", "street", "pew"]}

# --- calle: tránsito todo el primer compás y el ascenso
place(st["street"], traffic(9.0), 0, 1)
place(st["fx"], thump(), 0, .8); ev("heat", 0)
place(st["street"], bocina(), bt(1), .9); ev("bocina", 1)
c, _ = colectivo(1.6); place(st["street"], c, bt(1.6), 1.1); ev("bus", 1.6, dur=1.6)
place(st["fx"], thump(), bt(3), .6); ev("thermo", 3)
place(st["fx"], whoosh(BEAT * 1.0), bt(3.2), .5)

# --- groove de cumbia desde la negra 4 (la cámara empieza a subir)
for b in range(4, 32):
    if b in (19,):
        continue
    if b % 2 == 0:
        place(st["kick"], kick(.4), bt(b), .9); ev("kick", b)
    place(st["perc"], cowbell(), bt(b), .6 if b % 2 else .4)
    if b % 2 == 1:
        place(st["perc"], timbal(430, rim=True), bt(b), .7); ev("tac", b)
for s in range(8, 64):            # güira en corcheas: largo-corto-corto
    b = s / 2
    if 19 <= b < 20:
        continue
    place(st["perc"], guira(long=(s % 2 == 0)), bt(b), 1)
# bajo: 1 y 3 con la quinta en el "y" del 2 y del 4 (patrón típico)
for bar in range(1, 8):
    root, _ = CH[HARM[bar]]
    for off, nn in [(0, root), (1.5, root + 7), (2, root), (3.5, root + 7)]:
        b = bar * 4 + off
        if 19 <= b < 20:
            continue
        place(st["bass"], bass(nn - 12 if nn > 45 else nn, BEAT * .5), bt(b), 1)
place(st["bass"], bass(33, 2.4), bt(32), 1)
# acordeón: acordes a contratiempo + melodía
for bar in range(1, 8):
    _, notes = CH[HARM[bar]]
    for b in [.5, 1.5, 2.5, 3.5]:
        bb = bar * 4 + b
        if 19 <= bb < 20:
            continue
        place(st["acc"], accordion(notes, BEAT * .4, vib=False), bt(bb), .7)
MEL = [(4, .5, 76), (4.5, .5, 77), (5, 1, 76), (6, .5, 74), (6.5, .5, 72), (7, 1, 71),
       (8, .5, 74), (8.5, .5, 76), (9, 1, 74), (10, .5, 72), (10.5, .5, 71), (11, 1, 69),
       (12, .5, 72), (12.5, .5, 74), (13, 1, 72), (14, .5, 71), (14.5, .5, 69), (15, 1, 68),
       (16, .5, 71), (16.5, .5, 72), (17, .5, 74), (17.5, .5, 76), (18, 1, 77),
       (20, .5, 81), (20.5, .5, 79), (21, 1, 77), (22, .5, 76), (22.5, .5, 74), (23, 1, 76),
       (24, .5, 79), (24.5, .5, 77), (25, 1, 76), (26, .5, 74), (26.5, .5, 72), (27, 1, 74),
       (28, .5, 72), (28.5, .5, 71), (29, 1, 69), (30, .5, 71), (30.5, .5, 72), (31, 1, 69)]
for b, d, nn in MEL:
    place(st["acc"], accordion([nn], bt(d) * .92), bt(b), 1.0)

# --- pisos: cada llegada de la cámara = golpe + "pew" + escalón de cercanía
FLOORS = ["violeta", "caramelo", "fluo", "gris", "nude", "caramelo", "violeta", "fluo"]
for i, name in enumerate(FLOORS):
    b = 4 + i * 2
    place(st["pew"], pew(1400 + i * 120, 300), bt(b), .7)
    place(st["fx"], whoosh(BEAT * .9), bt(b) - BEAT * .85, .35)
    ev("floor", b, k=i + 1, to=name)
for i, (b, w) in enumerate([(4, "MIRÁ"), (6, "EL VERANO"), (8, "CON OTRO"), (10, "COLOR.")]):
    ev("word", b, i=i, w=w)
place(st["fx"], riser(BEAT * 2.5, 300, 9000), bt(17.5), .6); ev("riser", 17.5)
place(st["pew"], pew(2400, 120, .45), bt(19.4), .8)

# --- terraza: drop
place(st["fx"], impact(2.5), bt(20), .9); ev("drop", 20)
ev("word2", 20, i=0); ev("word2", 21, i=1)
for i in range(5):
    ev("flood", 20 + i * .5, i=i)
HANG = ["violeta", "caramelo", "fluo", "gris", "nude"]
for i, name in enumerate(HANG):
    b = 21 + i * .5
    place(st["perc"], timbal(560 + i * 60), bt(b), .6)
    ev("hang", b, i=i, to=name)

# --- etiquetas con número de serie
for i in range(5):
    b = 24 + i * .5
    place(st["perc"], cowbell(), bt(b), .5)
    ev("tag", b, i=i)
for i, b in enumerate([25, 26, 27]):
    ev("vline", b, i=i)

# --- tuyo y de nadie más
ev("yline", 28, i=0); ev("yline", 29, i=1)
place(st["fx"], whoosh(BEAT * 1.4), bt(30) - .1, .8); ev("unpin", 30)
place(st["pew"], pew(900, 1600, .3), bt(31), .5); ev("zoom", 31)

# --- cierre
place(st["fx"], impact(2.0), bt(32), .7); ev("final", 32)
place(st["acc"], accordion([57, 64, 69, 72], 3.0), bt(32), 1.1)
for i in range(8):
    ev("piece", 32 + i * .125, i=i)
ev("cta", 33, i=0); ev("cta", 34, i=1)
ev("sign", 34.5)
place(st["pew"], sparkle(81), bt(35.5), .7); ev("sparkle", 35.5)

# ----------------------------------------------------------------------------
# Mezcla: la cumbia se acerca piso por piso
# ----------------------------------------------------------------------------
def near(b):
    if b < 4: return 0.0
    if b >= 20: return 1.0
    k = sum(1 for i in range(8) if b >= 4 + i * 2)
    return .12 + .78 * k / 8


amt = np.array([near(b) for b in t_all / BEAT])
k_ = math.exp(-1 / (.08 * SR)); sm = np.empty(N); a = 0.0
for i, v in enumerate(amt):
    a = a * k_ + v * (1 - k_); sm[i] = a
amt = sm
side = np.ones(N)
for e in EVENTS:
    if e["kind"] in ("kick", "drop", "final"):
        i = int(e["t"] * SR); n = int(BEAT * SR); tt = np.arange(n) / SR
        j = min(N, i + n); side[i:j] = np.minimum(side[i:j], (1 - .4 * np.exp(-tt * 12))[: j - i])

music_L = st["kick"] * .9 + st["perc"] * .55 + st["bass"] * side * .7 + st["acc"] * side * .9 + st["fx"] * .45 + st["pew"] * .5
music_R = music_L.copy()
pp = .5 + .3 * np.sin(2 * np.pi * t_all / (BEAT * 2))
music_L += st["perc"] * .1 * np.cos(pp * np.pi / 2); music_R += st["perc"] * .1 * np.sin(pp * np.pi / 2)
send = st["acc"] * .5 + st["perc"] * .2 + st["pew"] * .4
music_L += convolve(send, synth_ir(1.8, 3.0, seed=7)) * .25
music_R += convolve(send, synth_ir(1.8, 3.0, seed=8)) * .25
# lejos = filtrado (como a través de una pared/ventana) + más bajo
cut = 350 * (20000 / 350) ** amt
music_L = svf(music_L, cut, q=.7) * (.35 + .65 * amt)
music_R = svf(music_R, cut, q=.7) * (.35 + .65 * amt)
# calle: fuerte abajo, se va quedando atrás al subir
street_g = np.clip(1.15 - amt * 1.1, 0, 1)
L = music_L + st["street"] * street_g
R = music_R + st["street"] * street_g * .9
mix = np.stack([L, R], 1)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.15)
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
