"use strict";
// ============================================================================
//  Activos de marca redibujados en vectores a partir de las piezas cargadas
//  (no había SVG oficial). Coordenadas en píxeles de las imágenes de referencia,
//  medidas columna por columna, así se pueden superponer y verificar.
// ============================================================================

// ---------------------------------------------------------------- TUPÉ
// Origen: esquina superior izquierda de la barra de la T (x=37, y=110 en la imagen
// de referencia de 201×251). Unidad = 1 px de esa imagen. Altura de caja: 0..30.
const TUPE = {
  w: 129, top: -11, bottom: 30,
  pieces: {
    bar: p => { p.rect(0, 0, 41.6, 3.5); },
    tStem: p => { p.moveTo(11, 0); p.lineTo(23, 0); p.lineTo(23, 24); p.arc(17, 24, 6, 0, Math.PI); p.closePath(); },
    u: p => {
      p.moveTo(31, 0); p.lineTo(41.8, 0); p.lineTo(41.8, 16.2); p.arc(45.4, 16.2, 3.6, Math.PI, 0, true); p.lineTo(49, 0); p.lineTo(59.4, 0);
      p.lineTo(59.4, 15.8); p.arc(45.2, 15.8, 14.2, 0, Math.PI); p.closePath();
    },
    pStem: p => { p.rect(61.8, 0, 11.2, 30); },
    pBowl: p => { p.moveTo(86, 10.4); p.arc(75.6, 10.4, 10.4, 0, Math.PI * 2); },
    eDome: p => {
      p.moveTo(87.2, 21); p.lineTo(87.2, 15.5); p.arc(102.8, 15.5, 15.6, Math.PI, Math.PI * 1.5 - 0.145);
      // ranura central (de la parte superior hasta v=13, fondo redondo)
      const sx0 = 100.6, sx1 = 105.6;
      p.lineTo(sx0, 0.2); p.lineTo(sx0, 13); p.arc(103.1, 13, 2.5, Math.PI, 0, true); p.lineTo(sx1, 0.2);
      p.arc(102.8, 15.5, 15.6, Math.PI * 1.5 + 0.18, Math.PI * 2);
      p.lineTo(118.4, 21); p.closePath();
    },
    eStem: p => { p.moveTo(87.2, 20.5); p.lineTo(99.4, 20.5); p.lineTo(99.4, 30); p.ellipse(99.4, 20.5, 12.2, 9.5, 0, Math.PI / 2, Math.PI); p.closePath(); },
    accent: p => { const x = 100.3, w = 6.4, y0 = -11, y1 = -0.6, r = w / 2; p.moveTo(x, y0 + r); p.arc(x + r, y0 + r, r, Math.PI, 0); p.lineTo(x + w, y1 - r); p.arc(x + r, y1 - r, r, 0, Math.PI); p.closePath(); },
  },
  order: ["bar", "tStem", "u", "pStem", "pBowl", "eDome", "eStem", "accent"],
};
function tupePath(name) { const p = new Path2D(); TUPE.pieces[name](p); return p; }
function drawCopyright(g, x, y, r, lw, col) {
  g.save(); g.strokeStyle = col; g.lineWidth = lw;
  g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.stroke();
  g.beginPath(); g.arc(x, y, r * .5, Math.PI * .25, Math.PI * 1.75); g.stroke();
  g.restore();
}

// ---------------------------------------------------------------- firma "Carla Di Sí"
// Trazos en orden de escritura. Coordenadas: x = columna − 132, y = fila − 218
// de la foto de producto (399×501). Cada trazo: [ancho, [[x,y]...]]
const SIGN = {
  w: 132, h: 26,
  strokes: [
    // C · a · r · l · a  (un solo gesto, como se escribe)
    [2.2, [[22.4, 14.3], [22.6, 10.5], [21.4, 7.2], [17.6, 6.1], [12.5, 7.3], [8.4, 10.6], [6, 15], [5.6, 19.2], [7, 22.6], [11, 24], [16.5, 23.8], [22, 22.6],
      [27.4, 21.7], [29.4, 19.6], [28, 17.4], [25.4, 17.2], [23.4, 19.2], [23.8, 21.8], [27.6, 21.7], [32.5, 20.4], [36.8, 19.3], [39.6, 19.6], [40.6, 21.5],
      [41.4, 23], [44.6, 22.8], [46.4, 18.5], [46.6, 12.5], [46.6, 7.4], [46.1, 12.5], [46, 18.5], [46.7, 22.4], [50, 23], [54.6, 22.6], [56.6, 20.2], [55.8, 17.6],
      [53.8, 17.1], [51.8, 19], [52.2, 21.8], [55.6, 23.3], [60.5, 23.8], [66.2, 24]]],
    // D: trazo superior que baja por la panza
    [2.5, [[64.2, 9], [70, 9.4], [76.5, 10], [82, 11], [85.6, 12.8], [87.8, 15.4], [89, 18], [90, 19.8]]],
    // D: asta
    [2.2, [[77.6, 14.2], [77.6, 18], [77.4, 21.5], [77.6, 23.2]]],
    // D: base que vuelve con un gancho
    [2.4, [[77.2, 22.4], [82, 20.7], [88, 20.1], [93.4, 20.2], [96, 21.3], [96.3, 23.2], [96, 24.6]]],
    // i de Di
    [2.2, [[94.8, 12.2], [95.1, 14.4]]],
    // S + í
    [2.3, [[117, 10.2], [111.5, 10.6], [105.5, 11.6], [101.2, 13.4], [101.5, 15.2], [106.5, 15.7], [112.5, 16.3], [117.2, 17.2], [120.8, 18.4], [123.2, 19.2],
      [119, 19.2], [114, 19.4], [110.6, 20.6], [110.6, 22.4], [113, 23.2], [116.4, 22.6], [118.2, 20.6], [120.6, 19.8], [123.8, 20.4], [124, 22.4], [123.9, 24.6]]],
    // tilde
    [2.0, [[129.2, 8.2], [128.2, 10.6], [127, 14.2]]],
  ],
};
// la base de la D y la panza de la S quedan ~1 px más abajo en el original
SIGN.strokes[3][1] = SIGN.strokes[3][1].map(([x, y]) => [x, y + .9]);
SIGN.strokes.forEach(s => s[0] *= .86);
// suaviza con Catmull-Rom y precalcula longitudes para el write-on
function catmull(pts, seg = 6) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let s = 0; s < seg; s++) {
      const t = s / seg, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(k => .5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
    }
  }
  out.push(pts[pts.length - 1]);
  return out;
}
SIGN.paths = SIGN.strokes.map(([w, pts]) => {
  const pp = catmull(pts, 8);
  let len = 0; const cum = [0];
  for (let i = 1; i < pp.length; i++) { len += Math.hypot(pp[i][0] - pp[i - 1][0], pp[i][1] - pp[i - 1][1]); cum.push(len); }
  return { w, pts: pp, len, cum };
});
SIGN.total = SIGN.paths.reduce((a, s) => a + s.len, 0);
// dibuja la firma con progreso p∈[0,1] (longitud total recorrida, en orden de escritura)
function drawSignature(g, x, y, scale, p, col, opts = {}) {
  g.save(); g.translate(x, y); g.scale(scale, scale);
  g.strokeStyle = col; g.lineCap = "round"; g.lineJoin = "round";
  let budget = p * SIGN.total;
  for (const s of SIGN.paths) {
    if (budget <= 0) break;
    const take = Math.min(budget, s.len); budget -= s.len;
    g.lineWidth = s.w * (opts.weight || 1);
    g.beginPath(); g.moveTo(s.pts[0][0], s.pts[0][1]);
    for (let i = 1; i < s.pts.length; i++) {
      if (s.cum[i] <= take) g.lineTo(s.pts[i][0], s.pts[i][1]);
      else { const a = (take - s.cum[i - 1]) / (s.cum[i] - s.cum[i - 1]); g.lineTo(s.pts[i - 1][0] + (s.pts[i][0] - s.pts[i - 1][0]) * a, s.pts[i - 1][1] + (s.pts[i][1] - s.pts[i - 1][1]) * a); break; }
    }
    g.stroke();
  }
  g.restore();
}
// punta de la pluma (para el destello que sigue al trazo)
function signatureTip(p) {
  let budget = p * SIGN.total;
  for (const s of SIGN.paths) {
    if (budget <= s.len) {
      for (let i = 1; i < s.pts.length; i++) if (s.cum[i] >= budget) {
        const a = (budget - s.cum[i - 1]) / Math.max(1e-6, s.cum[i] - s.cum[i - 1]);
        return [s.pts[i - 1][0] + (s.pts[i][0] - s.pts[i - 1][0]) * a, s.pts[i - 1][1] + (s.pts[i][1] - s.pts[i - 1][1]) * a];
      }
    }
    budget -= s.len;
  }
  const l = SIGN.paths[SIGN.paths.length - 1].pts; return l[l.length - 1];
}

// ---------------------------------------------------------------- anteojos cat-eye
// Medidos sobre el par naranja de la foto (perfil superior/inferior por columna).
// Coordenadas relativas al centro del puente (x=203, y=150 en la foto). Mitad izquierda;
// la derecha es su espejo.
const GL = {
  outer: [[-117.5, -47], [-103, -48.2], [-78, -47.8], [-53, -45.4], [-38, -42.2], [-27, -37.5], [-18, -30.5], [-12, -24.5], [-5, -23.1], [0, -23],
    [0, -9.5], [-6, -8.2], [-10, -0.5], [-14, 12], [-19, 25], [-27, 33], [-38, 40], [-53, 45.6], [-68, 45], [-83, 42.5], [-95, 36], [-103, 26],
    [-109, 13], [-113, 0], [-116, -12], [-117.5, -30]],
  lens: [[-108, -33], [-93, -34.5], [-73, -34.5], [-53, -33.5], [-38, -31.5], [-27, -28], [-20, -22], [-17, -12], [-18, 5], [-23, 20], [-33, 32],
    [-48, 40], [-65, 41.5], [-83, 40], [-97, 34], [-106, 22], [-110, 5], [-111, -15], [-110, -28]],
  hinge: [-117.5, -36, 9, 15],
};
function smoothClosed(pts, seg = 6) {
  const n = pts.length, out = [];
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    for (let s = 0; s < seg; s++) {
      const t = s / seg, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(k => .5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
    }
  }
  return out;
}
// contorno exterior completo: ala izq → borde superior → puente → ala der → inferior der → puente inferior → inferior izq
(function buildGlasses() {
  const L = GL.outer;
  const topLeft = L.slice(0, 10), botLeft = L.slice(10);
  const topRight = topLeft.slice(0, 9).reverse().map(([x, y]) => [-x, y]);
  const botRight = botLeft.slice(1).reverse().map(([x, y]) => [-x, y]);
  GL.outerFull = smoothClosed([...topLeft, ...topRight, ...botRight, ...botLeft], 4);
  GL.lensL = smoothClosed(GL.lens.map(([x, y]) => [-64 + (x + 64) * .935, y < -30 ? y + .8 : 2 + (y - 2) * .94]), 6);
  GL.lensR = GL.lensL.map(([x, y]) => [-x, y]);
})();
function polyPath(p, pts, ox = 0, oy = 0, sx = 1, sy = 1) {
  pts.forEach(([x, y], i) => i ? p.lineTo(ox + x * sx, oy + y * sy) : p.moveTo(ox + x * sx, oy + y * sy));
  p.closePath();
}
