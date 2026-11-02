"""
Recorta las fotos de producto del PPT (fondo blanco) y separa cada LENTE como capa propia.
Todo con numpy + PIL: crecimiento de regiones por dilatación, relleno de huecos, mate suavizado
y descontaminación del borde blanco. Uso:  python3 prep_assets.py <carpeta_media> <salida>
"""
import json
import sys

import numpy as np
from PIL import Image, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]


def dilate(m):
    d = m.copy()
    d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    return d


def grow(seed, allowed, max_iter=4000):
    r = seed & allowed
    for _ in range(max_iter):
        n = dilate(r) & allowed
        if n.sum() == r.sum():
            break
        r = n
    return r


def fill_holes(m):
    """devuelve m + todo lo que no está conectado al borde por fuera de m"""
    outside = np.zeros_like(m)
    outside[0, :] = outside[-1, :] = True
    outside[:, 0] = outside[:, -1] = True
    reach = grow(outside & ~m, ~m)
    return m | ~reach


def erode(m, k=1):
    for _ in range(k):
        e = m.copy()
        e[1:] &= m[:-1]; e[:-1] &= m[1:]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
        m = e
    return m


def dil(m, k=1):
    for _ in range(k):
        m = dilate(m)
    return m


def convex_hull(pts):
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# criterio de "lente" por color (cada acetato tiene otra relación con su lente)
PRODUCTS = {
    "violeta": dict(img="image2.jpg", line="lab001", crit=lambda r, g, b, L, S: (S < 34) & (L > 55) & (L < 205)),
    "caramelo": dict(img="image3.jpg", line="lab002", crit=lambda r, g, b, L, S: (L < 150) & (S < 48)),
    "fluo": dict(img="image4.jpg", line="lab002", crit=lambda r, g, b, L, S: (L < 155) & (S < 42)),
    "gris": dict(img="image5.jpg", line="lab002", crit=lambda r, g, b, L, S: ((r - b) > 40) & (L < 185)),
    "nude": dict(img="image6.jpg", line="lab001", crit=lambda r, g, b, L, S: (b >= r - 4) & (S < 34) & (L < 215)),
}

meta = {}


def cutout(a):
    """máscara del objeto: todo lo que no es el blanco puro del estudio"""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mn = np.minimum(np.minimum(r, g), b)
    mx = np.maximum(np.maximum(r, g), b)
    white = (mn >= 247) & ((mx - mn) < 9)
    border = np.zeros_like(white)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    bgm = grow(border & white, white)
    # huecos blancos encerrados (el ojo de cerradura sobre el puente): blanco puro, sin motas chicas
    pure = (mn >= 251)
    pure = dil(erode(pure, 3), 3)
    bgm |= pure
    return ~bgm


def matte(obj):
    m = Image.fromarray((obj * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    return np.asarray(m).astype(np.float32) / 255


def decontaminate(a, alpha):
    al = np.clip(alpha, 1e-3, 1)[..., None]
    c = (a - (1 - al) * 255) / al
    return np.clip(c, 0, 255)


for name, p in PRODUCTS.items():
    im = Image.open(f"{SRC}/{p['img']}").convert("RGB")
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = 0.299 * r + 0.587 * g + 0.114 * b
    S = np.max(a, -1) - np.min(a, -1)
    obj = cutout(a)
    crit = p["crit"](r, g, b, L, S) & obj
    seeds = np.zeros_like(crit)
    for fx in (.27, .73):
        sx, sy = int(w * fx), int(h * .6)
        seeds[sy - 3:sy + 3, sx - 3:sx + 3] = True
    lens = grow(seeds, crit)
    # cada lente por separado: rellenar huecos (patillas vistas a través) y suavizar
    lens = dil(erode(lens, 2), 2)
    # cada lente es convexo: su envolvente convexa tapa patillas y reflejos que el color no separa
    from PIL import ImageDraw
    hull_img = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(hull_img)
    for side in (np.s_[:, :w // 2], np.s_[:, w // 2:]):
        part = np.zeros_like(lens); part[side] = lens[side]
        ys_, xs_ = np.where(part)
        pts = sorted(set(zip(xs_[::7].tolist(), ys_[::7].tolist())))
        hull = convex_hull(pts)
        dr.polygon([tuple(p) for p in hull], fill=255)
    lens = (np.asarray(hull_img) > 0) & obj
    lens = erode(lens, 1)
    a_obj = matte(obj)
    a_lens = matte(lens) * a_obj
    rgb = decontaminate(a, a_obj)
    ys, xs = np.where(obj)
    x0, x1, y0, y1 = xs.min() - 6, xs.max() + 7, ys.min() - 6, ys.max() + 7
    x0, y0 = max(0, x0), max(0, y0)
    frame = np.dstack([rgb, np.clip(a_obj - a_lens, 0, 1) * 255]).astype(np.uint8)[y0:y1, x0:x1]
    lensl = np.dstack([rgb, a_lens * 255]).astype(np.uint8)[y0:y1, x0:x1]
    Image.fromarray(frame, "RGBA").save(f"{OUT}/frame_{name}.png", optimize=True)
    Image.fromarray(lensl, "RGBA").save(f"{OUT}/lens_{name}.png", optimize=True)
    # centros y cajas de cada lente (en coords del recorte)
    lys, lxs = np.where(lens[y0:y1, x0:x1])
    mid = (x1 - x0) / 2
    boxes = []
    for side in (lxs < mid, lxs >= mid):
        boxes.append([int(lxs[side].min()), int(lys[side].min()), int(lxs[side].max()), int(lys[side].max())])
    # color medio del acetato (para teñir el mundo a través del lente)
    fm = (a_obj > .9) & (a_lens < .1)
    col = a[fm].mean(0)
    meta[name] = dict(w=int(x1 - x0), h=int(y1 - y0), lens=boxes, frameColor=[int(c) for c in col], line=p["line"])
    print(name, meta[name], "lens px", int(lens.sum()))

# vista lateral (patilla grabada "lab002") y local
im = Image.open(f"{SRC}/image1.jpg").convert("RGB")
a = np.asarray(im).astype(np.float32)
obj = cutout(a)
al = matte(obj)
ys, xs = np.where(obj)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
Image.fromarray(np.dstack([decontaminate(a, al), al * 255]).astype(np.uint8)[y0:y1, x0:x1], "RGBA").save(f"{OUT}/side_fluo.png", optimize=True)
meta["side"] = dict(w=int(x1 - x0), h=int(y1 - y0))
Image.open(f"{SRC}/image7.jpg").save(f"{OUT}/local.jpg", quality=92)
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)

# versiones completas (montura + lente) y en gris: para el momento "de nadie más" y el local
for name in PRODUCTS:
    f = Image.open(f"{OUT}/frame_{name}.png"); l = Image.open(f"{OUT}/lens_{name}.png")
    full = Image.new("RGBA", f.size); full.alpha_composite(l); full.alpha_composite(f)
    full.save(f"{OUT}/full_{name}.png", optimize=True)
    g = full.convert("LA").convert("RGBA"); g.putalpha(full.getchannel("A"))
    g.save(f"{OUT}/fullgray_{name}.png", optimize=True)
Image.open(f"{OUT}/local.jpg").convert("L").convert("RGB").save(f"{OUT}/local_gray.jpg", quality=92)
