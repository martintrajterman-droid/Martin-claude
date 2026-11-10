import html, re, sys
lines = open(sys.argv[1], encoding="utf8").read().split("\n")[18:74]
H2 = {"Diagnóstico de la situación actual y escenario estratégico", "Análisis del bien vigente y estrategia de medios actual"}
blocks = []
for l in lines:
    l = l.strip()
    if not l: continue
    e = html.escape(l)
    if l in H2: blocks.append(("h", f"<h3>{e}</h3>", 120))
    elif len(l) < 60 and not l.endswith("."): blocks.append(("h", f"<h4>{e}</h4>", 90))
    else:
        m = re.match(r"^([A-ZÁÉÍÓÚ][^.:]{2,40}[.:]) (.*)$", l)
        if m and len(m.group(1)) < 42: e = f"<b>{html.escape(m.group(1))}</b> {html.escape(m.group(2))}"
        blocks.append(("p", f"<p>{e}</p>", len(l)))
pages, cur, size, LIM = [], [], 0, 4300
for i, (k, h, n) in enumerate(blocks):
    if size + n > LIM and cur:
        # no dejar un título huérfano al pie
        if cur and cur[-1][0] == "h": carry = [cur.pop()]
        else: carry = []
        pages.append(cur); cur, size = carry, sum(c[2] for c in carry)
    cur.append((k, h, n)); size += n
pages.append(cur)
out = []
for pi, pg in enumerate(pages):
    head = '<div class="kicker">Anexo · Diagnóstico de marca (Momento 2)</div>' + ('<h2>Anexo · Momento 2</h2>' if pi == 0 else '')
    body = "\n".join(h for _, h, _ in pg)
    out.append(f'<section class="page anexo">{head}{body}<div class="folio"><span>Anexo · Momento 2</span><span>{25 + pi}</span></div></section>')
src = open("carpeta_src.html", encoding="utf8").read()
css = "<style>.anexo p{font-size:8.6pt;line-height:1.45;margin-bottom:2mm}.anexo h3{margin-top:3mm}.anexo h4{margin-top:3mm}</style>"
open("build/carpeta.html", "w", encoding="utf8").write(src.replace("<!--ANEXO-->", css + "\n".join(out)))
print(len(pages), "páginas de anexo")
