"""
TUPÉ · "Mirá el verano con otro color" — versión REVELADO (20 s).
Disco-funk compuesto y sintetizado desde cero con numpy. La percusión del principio
es la propia cámara instantánea: carga del flash, disparo, avance de la película.

132 BPM · 11 compases = 44 negras = exactamente 20,000 s.
Gesto sonoro: el arranque es "en blanco y negro" (solo ritmo de cámara). Cada foto que
se revela agrega un color a la música: bajo, clavinet, cuerdas, vientos.
"""
import json
import math
import sys
import wave

import numpy as np

from dsp import SR, rng, midi, place, env_adsr, svf, onepole_hp, polyblep_saw, kick, clap, riser, impact, synth_ir, convolve

BPM = 132.0
BEAT = 60 / BPM
DUR = 20.0
N = int(SR * DUR)
t_all = np.arange(N) / SR
bt = lambda b: b * BEAT
EVENTS = []


def ev(kind, b, **kw):
    EVENTS.append(dict(kind=kind, t=round(bt(b), 6), b=b, **kw))


# ----------------------------------------------------------------------------
# Cámara instantánea (todo síntesis)
# ----------------------------------------------------------------------------
def click(f=4200, dec=260, amp=1.0):
    n = int(.03 * SR); t = np.arange(n) / SR
    return svf(rng.standard_normal(n), f, q=2.2, mode="bp") * np.exp(-t * dec) * amp


def shutter():
    """espejo que sube y baja: dos clics + golpe mecánico"""
    out = np.zeros(int(.12 * SR))
    place(out, click(3800, 300, 1.0), 0)
    place(out, click(2600, 220, .8), .045)
    n = int(.08 * SR); t = np.arange(n) / SR
    place(out, np.sin(2 * np.pi * 140 * t) * np.exp(-t * 60) * .6, 0)
    return out * .8


def winder(steps=6, span=.22):
    """avance de la película: trinquete"""
    out = np.zeros(int((span + .05) * SR))
    for i in range(steps):
        place(out, click(5200 + 300 * (i % 2), 400, .5 + .1 * (i % 2)), i * span / steps)
    return out


def flash_whine(length=1.0):
    """carga del flash: seno que sube hasta casi ultrasonido"""
    n = int(length * SR); t = np.arange(n) / SR; p = t / length
    f = 900 * (7500 / 900) ** p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * p ** 1.5 * .12


def flash_pop():
    n = int(.25 * SR); t = np.arange(n) / SR
    pop = svf(rng.standard_normal(n), 6000, q=.7) * np.exp(-t * 45)
    th = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 14)
    return pop * .7 + th * .6


def eject():
    """la foto sale por la ranura: motorcito + fricción"""
    n = int(.35 * SR); t = np.arange(n) / SR
    motor = np.sign(np.sin(2 * np.pi * 180 * t)) * .15 + np.sin(2 * np.pi * 360 * t) * .1
    fr = svf(rng.standard_normal(n), 2000, q=1, mode="bp") * .2
    return svf(motor + fr, 1800, q=.7) * np.sin(np.pi * t / .35) ** .8 * .6


# ----------------------------------------------------------------------------
# Banda disco-funk
# ----------------------------------------------------------------------------
def ks(note, length=.4, bright=.8, decay=.993):
    n = int(length * SR); f = midi(note); L = max(2, int(round(SR / f)))
    buf = rng.uniform(-1, 1, L)
    for _ in range(int((1 - bright) * 4)): buf = .5 * (buf + np.roll(buf, 1))
    out = np.empty(n); b = buf.tolist(); i = 0
    for s in range(n):
        j = (i + 1) % L; v = decay * .5 * (b[i] + b[j]); out[s] = b[i]; b[i] = v; i = j
    return out * .5


def clav(note, length=.18):
    """clavinet: cuerda pulsada + filtro de pastilla + wah"""
    s = ks(note, length + .05, .95, .985)
    n = len(s); t = np.arange(n) / SR
    return svf(s, 900 + 2600 * np.exp(-t * 18), q=3.2, mode="bp") * 2.2 * np.clip((length + .05 - t) / .03, 0, 1)


def bass(note, length):
    n = int((length + .04) * SR); t = np.arange(n) / SR; f = midi(note)
    s = polyblep_saw(np.full(n, f), n) * .7 + np.sin(2 * np.pi * f * t)
    s = svf(s, 220 + 1400 * np.exp(-t * 22), q=1.6)
    return np.tanh(s * env_adsr(n, .003, .06, .6, .03, length) * 1.8) * .6


def strings(notes, length, att=.15):
    n = int((length + .4) * SR); L = np.zeros(n); R = np.zeros(n)
    for note in notes:
        f = midi(note)
        for v in range(5):
            d = (v - 2) / 2
            s = polyblep_saw(np.full(n, f * (1 + d * .006)), n, phase0=rng.random())
            pan = .5 + d * .4
            L += s * math.cos(pan * math.pi / 2); R += s * math.sin(pan * math.pi / 2)
    e = env_adsr(n, att, .2, .8, .3, length)
    g = .05 / len(notes) * 3
    return svf(L, 3200, q=.7) * e * g, svf(R, 3200, q=.7) * e * g


def brass(notes, length):
    n = int((length + .1) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for note in notes:
        f = midi(note) * (1 + .01 * np.exp(-t * 30))
        s += polyblep_saw(f, n) + .4 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    s = svf(s, 600 + 3800 * np.exp(-t * 9) * np.clip(t / .02, 0, 1), q=1.1)
    return s * env_adsr(n, .015, .1, .7, .06, length) * .12 / len(notes) * 2


def hat(open_=False):
    n = int((.16 if open_ else .04) * SR); t = np.arange(n) / SR
    return onepole_hp(rng.standard_normal(n), 8000) * np.exp(-t * (18 if open_ else 110)) * .45


def sparkle(base):
    out = np.zeros(int(1.0 * SR))
    for i, nn in enumerate([0, 7, 12, 16, 19, 24]):
        place(out, ks(base + nn, .6, .95, .995) * (.6 - i * .07), i * .04)
    return out


# ----------------------------------------------------------------------------
# Partitura (Re dórico: Dm9 · G13, se resuelve en Fa 6/9)
# ----------------------------------------------------------------------------
st = {k: np.zeros(N) for k in ["cam", "kick", "clap", "hats", "bass", "clav", "brass", "fx"]}
strL, strR = np.zeros(N), np.zeros(N)
CH = [("Dm9", 38, [60, 64, 65, 69], [62, 65, 69, 72]), ("G13", 43, [59, 64, 65, 69], [65, 67, 71, 74])]

# --- oscuridad, carga del flash, disparo
place(st["fx"], flash_whine(bt(2)), 0, 1); ev("whine", 0)
place(st["fx"], flash_pop(), bt(2), 1); ev("flash", 2)
# disparos: cada uno expulsa una foto
SHOTS = [(3, "caramelo"), (7, "fluo"), (11, "violeta"), (13, "gris"), (15, "nude")]
for i, (b, name) in enumerate(SHOTS):
    place(st["cam"], shutter(), bt(b), 1); place(st["fx"], flash_pop() * .5, bt(b), .6)
    place(st["cam"], eject(), bt(b) + .06, .8)
    ev("shot", b, i=i, to=name)
    ev("land", b + 1, i=i, to=name)                    # la foto cae en la mesa en la negra siguiente
    ev("developed", b + (3.5 if i < 2 else 2.5), i=i)   # revelado completo

# --- ritmo de cámara (blanco y negro): obturador en 2 y 4, avance en el contratiempo
for b in range(4, 20):
    if b % 2 == 1 and b not in [s for s, _ in SHOTS]:
        place(st["cam"], shutter(), bt(b), .55); ev("snap", b)
    place(st["cam"], winder(3, .1), bt(b + .5), .5)
for b in range(4, 44):
    if b in (19,) or b >= 42:
        continue
    place(st["kick"], kick(.35), bt(b), .9 if b >= 20 else (.32 if b < 8 else .5)); ev("kick", b)

# --- capas de color: cada foto revelada suma un instrumento
LAYER = {"bass": 8, "clav": 12, "strings": 15, "full": 20}
for b in range(LAYER["bass"], 42):
    if 19 <= b < 20:
        continue
    root = CH[(b // 4) % 2][1]
    for off, nn in [(0, root), (.5, root + 12), (1, root), (1.5, root + 12)][:2]:
        place(st["bass"], bass(nn, BEAT * .42), bt(b + off), 1)
CLAV_PAT = [0, .75, 1.5, 2.25, 2.5, 3.25]
for bar in range(3, 10):
    for off in CLAV_PAT:
        b = bar * 4 + off
        if b < LAYER["clav"] or 19 <= b < 20:
            continue
        notes = CH[bar % 2][3]
        place(st["clav"], clav(notes[int(off * 4) % len(notes)], .14), bt(b), 1)
for bar in range(3, 10):
    if bar * 4 + 4 <= LAYER["strings"]:
        continue
    l, r = strings(CH[bar % 2][2], bt(4) * .95, .25 if bar < 5 else .04)
    st0 = max(bar * 4, LAYER["strings"])
    place(strL, l[int((bt(st0) - bt(bar * 4)) * SR):], bt(st0), 1); place(strR, r[int((bt(st0) - bt(bar * 4)) * SR):], bt(st0), 1)
for b in range(20, 42):
    place(st["hats"], hat(False), bt(b), .6); place(st["hats"], hat(True), bt(b + .5), .7)
    place(st["hats"], hat(False), bt(b + .25), .3); place(st["hats"], hat(False), bt(b + .75), .3)
    if b % 2 == 1:
        place(st["clap"], clap(), bt(b), .7)
# vientos: el riff del drop
HORN = [(20, .5, [74, 77]), (20.75, .25, [72, 76]), (21.5, .5, [74, 77]), (22.5, .25, [77, 81]), (23, 1, [76, 79]),
        (24, .5, [74, 77]), (24.75, .25, [72, 76]), (25.5, .5, [74, 77]), (26.5, .5, [79, 83]), (27, 1, [77, 81])]
for b, d, notes in HORN:
    place(st["brass"], brass(notes, bt(d)), bt(b), 1); ev("horn", b)

# --- ráfaga de flashes (corcheas) antes del drop
for i in range(8):
    b = 16 + i * .5
    if b >= 19.5:
        break
    place(st["cam"], shutter(), bt(b), .7); place(st["fx"], flash_pop() * .4, bt(b), .6)
    ev("burst", b, i=i)
place(st["fx"], riser(BEAT * 3.5, 300, 9000), bt(16.5), .6); ev("riser", 16.5)
place(st["fx"], flash_whine(bt(1)), bt(19), .9)

# --- DROP
place(st["fx"], impact(2.4), bt(20), .9); place(st["fx"], flash_pop(), bt(20), 1); ev("drop", 20)
ev("word2", 20, i=0); ev("word2", 21, i=1)
for i, name in enumerate(["violeta", "caramelo", "fluo", "gris", "nude"]):
    b = 22 + i * .5
    ev("place", b, i=i, to=name)
ev("obj", 24, which="case"); ev("obj", 24.5, which="cloth"); ev("obj", 25, which="lemon")
place(st["cam"], winder(6, .2), bt(24), .5)

# --- certificado de serie
place(st["fx"], flash_pop() * .4, bt(26), .5); ev("cert", 26)
for i, b in enumerate([27, 28, 29]):
    place(st["cam"], click(1800, 160, 1.2), bt(b), .9); ev("stamp", b, i=i)

# --- tuyo y de nadie más (respiro: sin bombo dos negras)
ev("yline", 30, i=0); ev("yline", 31, i=1)
place(st["fx"], flash_pop() * .5, bt(32), .6); ev("choose", 32)

# --- cierre: el cierre mismo es una foto que se revela
place(st["fx"], flash_whine(bt(1.6)), bt(32.4), .8)
place(st["cam"], shutter(), bt(34), 1); place(st["fx"], impact(2.0), bt(34), .7); place(st["fx"], flash_pop(), bt(34), 1); ev("endshot", 34)
place(st["cam"], eject(), bt(34) + .06, .9)
l, r = strings([53, 57, 62, 67, 69], 4.0, .3)
place(strL, l, bt(34), 1.1); place(strR, r, bt(34), 1.1)
place(st["bass"], bass(29, 3.5), bt(34), 1.0)
ev("enddev", 35); ev("cta", 37, i=0); ev("cta", 38, i=1)
place(st["clav"], clav(77, .3), bt(37), 1); place(st["clav"], clav(81, .3), bt(38), 1)
place(st["cam"], eject(), bt(39) - .15, .6); ev("store", 39)
ev("caption", 40); ev("sign", 40.5)
place(st["fx"], sparkle(77), bt(43), .6); ev("sparkle", 43)

# ----------------------------------------------------------------------------
# Mezcla
# ----------------------------------------------------------------------------
side = np.ones(N)
for e in EVENTS:
    if e["kind"] == "kick" and e["b"] >= 20:
        i = int(e["t"] * SR); n = int(BEAT * SR); tt = np.arange(n) / SR
        j = min(N, i + n); side[i:j] = np.minimum(side[i:j], (1 - .45 * np.exp(-tt * 12))[: j - i])
dry = st["kick"] * .9 + st["clap"] * .4 + st["hats"] * .3 + st["bass"] * side * .7 + st["fx"] * .5 + st["cam"] * .7
pp = .5 + .3 * np.sin(2 * np.pi * t_all / (BEAT * 2))
L = dry + st["clav"] * .55 * np.cos(pp * np.pi / 2) + st["brass"] * .8 + strL * side
R = dry + st["clav"] * .55 * np.sin(pp * np.pi / 2) + st["brass"] * .8 + strR * side
send = st["clav"] * .3 + st["brass"] * .4 + (strL + strR) * .15 + st["clap"] * .25
L += convolve(send, synth_ir(1.6, 3.2, seed=9)) * .28
R += convolve(send, synth_ir(1.6, 3.2, seed=10)) * .28
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
