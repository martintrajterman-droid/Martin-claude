"""
TUPÉ · "Mirá el verano con otro color" — versión PERSIANAS (20 s).
Pop surf compuesto y sintetizado desde cero con numpy: guitarra por síntesis
Karplus-Strong (una cuerda simulada), bajo pulsado, órgano aditivo con leslie,
batería y reverb de resorte sintética. Sin samples.

120 BPM · 10 compases = 40 negras = exactamente 20,000 s.
El gris suena a RADIO AM (banda angosta, mono, crujidos). Cada tira que gira al
color sube la radio un escalón hacia el hi-fi. Eventos → build/score.json.
"""
import json
import math
import sys
import wave

import numpy as np

from dsp import SR, rng, midi, place, env_adsr, svf, onepole_hp, kick, clap, riser, impact, convolve

BPM = 120.0
BEAT = .5
BAR = 2.0
DUR = 20.0
N = int(SR * DUR)
t_all = np.arange(N) / SR
bt = lambda b: b * BEAT
EVENTS = []


def ev(kind, b, **kw):
    EVENTS.append(dict(kind=kind, t=round(bt(b), 6), b=b, **kw))


# ----------------------------------------------------------------------------
# Karplus-Strong: ruido en una línea de retardo que se promedia a sí misma = cuerda
# ----------------------------------------------------------------------------
def ks(note, length=1.0, bright=.6, decay=.996, pick=.5):
    n = int(length * SR)
    f = midi(note)
    L = max(2, int(round(SR / f)))
    buf = rng.uniform(-1, 1, L)
    # posición de la púa: filtro peine sobre la excitación
    k = int(L * pick * .5)
    buf = buf - np.roll(buf, k) * .7
    # brillo de la púa: suavizado inicial
    for _ in range(int((1 - bright) * 4)):
        buf = .5 * (buf + np.roll(buf, 1))
    out = np.empty(n)
    b = buf.tolist(); i = 0
    for s in range(n):
        j = (i + 1) % L
        v = decay * .5 * (b[i] + b[j])
        out[s] = b[i]; b[i] = v; i = j
    return out * .5


def snare():
    n = int(.25 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 185 * t * (1 + .3 * np.exp(-t * 60))) * np.exp(-t * 22)
    nz = svf(rng.standard_normal(n), 4200, q=.8) * np.exp(-t * 18)
    return np.tanh((body * .7 + nz) * 1.4) * .7


def hat(open_=False):
    n = int((.18 if open_ else .045) * SR)
    t = np.arange(n) / SR
    x = onepole_hp(rng.standard_normal(n), 7500)
    return x * np.exp(-t * (16 if open_ else 95)) * .5


def tamb():
    n = int(.12 * SR)
    t = np.arange(n) / SR
    metal = sum(np.sin(2 * np.pi * f * t) for f in [5200, 6700, 8100, 9300]) * .15
    x = onepole_hp(rng.standard_normal(n), 5000) + metal
    return x * (1 - np.exp(-t * 500)) * np.exp(-t * 30) * .35


def organ(notes, length):
    """órgano de drawbars (16' 8' 4' 2 2/3') con leslie (AM + FM lenta)"""
    n = int((length + .1) * SR)
    t = np.arange(n) / SR
    les = 2 * np.pi * 6.2 * t
    s = np.zeros(n)
    for note in notes:
        f = midi(note)
        for mult, amp in [(.5, .5), (1, 1), (2, .55), (3, .35), (4, .2)]:
            s += amp * np.sin(2 * np.pi * f * mult * t + .004 * f * mult / 100 * np.sin(les))
    s *= (1 + .18 * np.sin(les)) / len(notes)
    e = env_adsr(n, .01, .05, .9, .08, length)
    return s * e * .11


def tick():
    n = int(.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2800 * t) * np.exp(-t * 220) * .5


def chk():
    """deslizamiento seco de una tira"""
    n = int(.09 * SR); t = np.arange(n) / SR
    return svf(rng.standard_normal(n), 1800 + 4000 * t / .09, q=2, mode="bp") * np.exp(-t * 35) * .8


def fwip(length=.18):
    """giro de persiana"""
    n = int(length * SR); t = np.arange(n) / SR; p = t / length
    s = svf(rng.standard_normal(n), 600 + 7000 * p, q=1.5, mode="bp") * np.sin(np.pi * p) ** 1.2
    return s * .9


def flap(count=10):
    """cartel split-flap: ráfaga de clics plásticos"""
    out = np.zeros(int((count * .045 + .2) * SR))
    for i in range(count):
        n = int(.02 * SR); t = np.arange(n) / SR
        c = svf(rng.standard_normal(n), 3000 + rng.random() * 1500, q=3, mode="bp") * np.exp(-t * 300)
        place(out, c, i * .045 * (1 - .3 * i / count), .7 + .3 * rng.random())
    return out


def spring_ir(length=1.6):
    """reverb de resorte: ruido con dispersión (chirp descendente) y rebotes"""
    n = int(length * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.2)
    chirp = np.sin(2 * np.pi * (2400 * t - 900 * t * t)) * np.exp(-t * 6) * .6
    for d in [.032, .061, .094]:
        i = int(d * SR); ir[i:] += chirp[: n - i] * .5
    ir = svf(ir, 4500, q=.8)
    return ir / np.sqrt(np.sum(ir ** 2))


def sparkle(base):
    out = np.zeros(int(1.0 * SR))
    for i, nn in enumerate([0, 7, 12, 16, 19, 24]):
        place(out, ks(base + nn, .7, .9, .994) * (.7 - i * .08), i * .04)
    return out


# ----------------------------------------------------------------------------
# Partitura: Re mayor surf. D · Bm · G · A · Em7→A7 · D(drop) · Bm · G · A · D
# ----------------------------------------------------------------------------
CH = {"D": (38, [62, 66, 69]), "Bm": (35, [62, 66, 71]), "G": (43, [62, 67, 71]), "A": (45, [61, 64, 69]),
      "Em7": (40, [62, 67, 71]), "A7": (45, [61, 67, 69])}
HARM = ["D", "Bm", "G", "A", "Em7", "D", "Bm", "G", "A", "D"]
st = {k: np.zeros(N) for k in ["kick", "snare", "hats", "bass", "gtr", "organ", "fx", "clap"]}

# --- compás 1: el verano en la radio; se cortan las tiras
place(st["kick"], kick(.4), 0, .9); ev("sun", 0)
for i, b in enumerate([1, 1.5, 2, 2.5]):
    place(st["fx"], tick(), bt(b), .7); ev("line", b, i=i)
place(st["fx"], chk(), bt(3), .9); ev("shift", 3)
place(st["fx"], chk(), bt(3.5), .7); ev("align", 3.5)

# --- batería desde la negra 4 (con huecos de arreglo)
for b in range(4, 40):
    if b in (19,) or b >= 36:
        continue
    place(st["kick"], kick(.4), bt(b), .95 if b % 2 == 0 else .8); ev("kick", b)
    if b % 2 == 1 and b != 19:
        place(st["snare"], snare(), bt(b), .8); ev("snare", b)
for s in range(8, 72):
    b = s / 2
    if 19 <= b < 20:
        continue
    place(st["hats"], hat(s % 4 == 3), bt(b), .7 if s % 2 == 0 else .5)
for s in range(80, 112):              # pandereta en semicorcheas en el drop
    place(st["hats"], tamb(), bt(s / 4), 1 if s % 2 else .5)

# --- bajo (Karplus-Strong grave, octava y quinta)
for bar in range(2, 10):
    root, _ = CH[HARM[bar]]
    if bar == 4:
        pat = [(0, root), (1, root + 7), (2, CH["A7"][0]), (3, CH["A7"][0] + 7)]
    else:
        pat = [(0, root), (.75, root), (1.5, root + 7), (2, root + 12), (3, root + 7), (3.5, root)]
    for off, nn in pat:
        b = bar * 4 + off
        if 19 <= b < 20:
            continue
        place(st["bass"], ks(nn, .55, .35, .992, .3), bt(b), 1)

# --- órgano a contratiempo (el "skank" del surf-pop)
for bar in range(1, 10):
    _, notes = CH[HARM[bar]]
    for b in range(4):
        bb = bar * 4 + b + .5
        if 19 <= bb < 20 or bb > 36:
            continue
        place(st["organ"], organ(notes, .22), bt(bb), 1)
place(st["organ"], organ([62, 66, 69, 74], 3.0), bt(36), 1.2)

# --- giros de persiana: cada uno es una nota de guitarra y un escalón hacia el hi-fi
FLIPS = [9, 9.5, 10, 10.5, 11]
for i, b in enumerate(FLIPS):
    place(st["fx"], fwip(), bt(b) - .06, .5)
    place(st["gtr"], ks([69, 71, 74, 76, 78][i], 1.2, .8, .996), bt(b), .9)
    ev("flip", b, i=i)
place(st["fx"], chk(), bt(8), .9); ev("textswap", 8)
for i, b in enumerate([4, 5, 6]):
    place(st["fx"], chk(), bt(b) - .04, .6); ev("word", b, i=i)
ev("glitch", 7)
ev("labels", 11.5)

# --- riff surf de guitarra (tremolo picking) en la cinta transportadora
RIFF = [(12, 74), (12.5, 73), (13, 71), (13.5, 69), (14, 71), (14.5, 74), (15, 76), (15.5, 78)]
for b, nn in RIFF:
    place(st["gtr"], ks(nn, .5, .85, .994), bt(b), .8); ev("riff", b, midi=nn)

# --- compás 5: se barajan los colores en corcheas + riser
for i in range(8):
    b = 16 + i * .5
    if b >= 19.5:
        break
    place(st["fx"], fwip(.12), bt(b) - .03, .35)
    place(st["gtr"], ks([66, 69, 71, 74, 76, 78, 81][i % 7], .4, .9, .993), bt(b), .7)
    ev("shuffle", b, i=i)
place(st["fx"], riser(BEAT * 3, 300, 9000), bt(17), .6); ev("riser", 17)
ev("collapse", 19.5)

# --- DROP: cortes de color-blocking
place(st["fx"], impact(2.4), bt(20), .9)
CUT_ORDER = [(20, "fluo"), (21, "violeta"), (22, "caramelo"), (22.5, "gris"), (23, "nude"), (23.5, "fluo")]
for b, name in CUT_ORDER:
    ev("cut", b, to=name)
    place(st["gtr"], ks({"fluo": 81, "violeta": 78, "caramelo": 76, "gris": 74, "nude": 78}[name], .8, .9, .995), bt(b), .7)
ev("word2", 20, i=0); ev("word2", 21, i=1)

# --- valor: split-flap
place(st["fx"], flap(14), bt(24), .8); ev("flap", 24)
place(st["gtr"], ks(78, 1.4, .8, .997), bt(25), .7); ev("flap_land", 25)
for i, b in enumerate([25, 26, 27]):
    ev("vline", b, i=i)

# --- macro del acetato, tuyo y de nadie más
ev("macro", 28)
ev("yline", 28.5, i=0); ev("yline", 29.5, i=1)
place(st["fx"], fwip(.25), bt(30) - .05, .6); ev("choose", 30)
place(st["clap"], clap(), bt(30), .6)

# --- cierre: persianas que bajan, logo, local que gira al color
for i in range(5):
    b = 32 + i * .25
    place(st["fx"], fwip(.12), bt(b) - .03, .4); ev("slat", b, i=i)
place(st["fx"], impact(2.0), bt(33.25), .6)
for i in range(8):
    ev("piece", 33.25 + i * .125, i=i)
place(st["gtr"], ks(74, 1.2, .8, .996), bt(34), .7); ev("cta", 34, i=0)
place(st["gtr"], ks(78, 1.2, .8, .996), bt(35), .7); ev("cta", 35, i=1)
for i in range(5):
    b = 36 + i * .25
    place(st["fx"], fwip(.1), bt(b) - .03, .3)
    place(st["gtr"], ks([74, 78, 81, 86, 90][i], .7, .9, .995), bt(b), .55)
    ev("pflip", b, i=i)
ev("sign", 37.5)
place(st["fx"], sparkle(74), bt(39), .5); ev("sparkle", 39)


# ----------------------------------------------------------------------------
# Mezcla: radio AM → hi-fi
# ----------------------------------------------------------------------------
def hifi_amt(b):
    a = 0.0
    for i, fb in enumerate(FLIPS):
        if b >= fb: a = (i + 1) / 5 * .85
    if b >= 20: a = 1.0
    return a


amt = np.array([hifi_amt(b) for b in t_all / BEAT])
k = math.exp(-1 / (.04 * SR)); sm = np.empty(N); a = 0.0
for i, v in enumerate(amt):
    a = a * k + v * (1 - k); sm[i] = a
amt = sm

side = np.ones(N)
for e in EVENTS:
    if e["kind"] == "kick":
        i = int(e["t"] * SR); n = int(BEAT * SR); tt = np.arange(n) / SR
        j = min(N, i + n); side[i:j] = np.minimum(side[i:j], (1 - .45 * np.exp(-tt * 12))[: j - i])

gtr = st["gtr"] * (1 + .35 * np.sin(2 * np.pi * 7.5 * t_all))      # trémolo surf
dry = st["kick"] * .9 + st["snare"] * .45 + st["hats"] * .3 + st["bass"] * side * .7 + st["fx"] * .5 + st["clap"] * .4
pp = .5 + .3 * np.sin(2 * np.pi * t_all / 2.0)
L = dry + gtr * .55 * np.cos(pp * np.pi / 2) + st["organ"] * side * .9
R = dry + gtr * .55 * np.sin(pp * np.pi / 2) + st["organ"] * side * .75
spr = spring_ir()
send = gtr * .7 + st["snare"] * .25 + st["organ"] * .2
L += convolve(send, spr) * .35
R += convolve(send, np.roll(spr, 37)) * .35

# versión radio: mono, banda 350–2800 Hz, saturada, con crujidos
mono = (L + R) / 2
radio = svf(svf(mono, 2800, q=.9), 350, q=.7, mode="hp")
radio = np.tanh(radio * 2.2) * .5
crackle = np.zeros(N)
pops = rng.random(N) < 18 / SR
crackle[pops] = rng.standard_normal(pops.sum()) * .5
crackle = svf(crackle, 3000, q=1, mode="bp") + svf(rng.standard_normal(N), 1500, q=.6, mode="bp") * .012
radio = radio + crackle

hl, hr = L / np.max(np.abs(L)), R / np.max(np.abs(R))
radio = radio / np.max(np.abs(radio)) * 1.05
Lm = radio * (1 - amt) + hl * amt
Rm = radio * (1 - amt) + hr * amt
mix = np.stack([Lm, Rm], 1)
mix = np.tanh(mix * 1.1)
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
