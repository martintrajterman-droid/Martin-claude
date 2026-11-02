# DECISIONES — TUPÉ · "Mirá el verano con otro color" · versión FÁBRICA (20 s)

**Entregable:** `tupe6/tupe_fabrica_20s.mp4`, H.264 High, 1080×1920, 60 fps, AAC estéreo a 48 kHz, 20,000 s.
**Materiales:** los recortes de las fotos del PPT *TUPÉ · momento.02* (los cinco colores y el local) y los datos del brief. Todo lo demás es código: la cortadora láser, las planchas, las chispas, el tambor y la patilla son vectores, y la música está sintetizada desde cero. No usé modelos de imagen, vídeo ni audio, ni samples.

---

## 1. Idea: de dónde sale el color

Las versiones anteriores mostraban el verano de afuera: la playa, la ciudad, las fotos. Esta va **adentro del objeto**. El FODA del PPT pone como fortaleza la **"fábrica propia: tiradas cortas"**, y en el contexto aparece "fábrica propia en CABA". Por eso el escenario es el taller.

**El mecanismo nuevo es que debajo del gris hay color.** Una plancha de acetato gris entra a la cortadora láser y el láser corta un cat-eye. **Donde corta, asoma el color**: la ranura brilla en mandarina, la pieza se llena, se levanta y se convierte en el TUPÉ real de la foto. El color no se agrega desde afuera: estaba adentro y el oficio lo saca.

| | Playa | Persianas | Ciudad | Revelado | **Fábrica** |
|---|---|---|---|---|---|
| Punto de partida | playa | playa en tiras | calle | sala oscura | **taller apagado** |
| Cómo entra el color | lente-ventana | giro de tiras | inundación por piso | revelado químico | **el corte del láser lo descubre** |
| Música | balear | surf | cumbia | disco-funk | **techno ácido que nace de la máquina** |
| Gesto sonoro | filtro | radio → hi-fi | se acerca | suma instrumentos | **los motores de la máquina tocan la melodía** |

## 2. Estructura (144 BPM · 12 compases = 48 negras = 20,000 s)

| Negras | Tiempo | Qué pasa | Golpe |
|---|---|---|---|
| 0–3 | 0–1,25 s | Taller a oscuras. Se prenden los tubos con los parpadeos del arrancador y aparece la cama de la cortadora (panal de metal) | zumbido de 100 Hz y clics del arrancador |
| 3–4 | 1,25–1,7 s | Entra la plancha de acetato gris y la sujetan las mordazas | *whoosh*, dos golpes metálicos |
| 4–8 | 1,7–3,3 s | **Grabado láser** de "MIRÁ EL / VERANO", línea por línea, con el cabezal barriendo y chispas | un *zap* de láser por semicorchea |
| 8–14 | 3,3–5,8 s | **El láser corta el frente cat-eye**: la ranura asoma mandarina mientras el pórtico sigue al cabezal. **Los motores paso a paso tocan la melodía**, una nota por corchea | 12 notas de motor, zumbido del láser |
| 14–15 | 5,8–6,25 s | Se completa el corte, **la pieza se llena de color**, se levanta y se transforma en el **lab002 caramelo real** | *zap* final, *whoosh* |
| 16–24 | 6,7–10 s | **Carrusel**: cuatro planchas más (flúo, violeta, gris, nude), una cada dos negras. Cada una se corta en una negra y su pieza vuela. "CON OTRO / COLOR." | golpe de mordaza, arpegio de 4 notas de motor, *zap* |
| 24–32 | 10–13,3 s | **DROP · "¡QUÉ TUPÉ!"**: el **tambor de pulido** gira con los cinco TUPÉ adentro y brillos de pulido. En cada negra el tambor da un empujón y **la nave se tiñe del color del modelo siguiente** | impacto, techno ácido (línea tipo 303), piezas rodando |
| 32–38 | 13,3–15,8 s | Primer plano de una patilla de acetato negro con "lab002" ya grabado: **el láser graba "N° 07/24"**. Debajo: "N° de serie en la patilla" · "21–24 piezas por color." · "Fábrica propia en CABA · 100% acetato argentino" | zumbido del láser, un golpe de taller por línea |
| 38–40 | 15,8–16,7 s | "Un anteojo que es tuyo / y de nadie más." con el flúo arriba | — |
| 40–48 | 16,7–20 s | Cierre: **el láser recorta el logo TUPÉ©** de arriba abajo, con chispas mandarina. Luego *encontrá* / *en carladisi.com/tupe*, el local, "Probalos en Palermo Soho", firma y destello | impacto, *zap* por semicorchea, *sparkle* |

## 3. Decisiones

- **El taller como verdad de marca**: "Hecho en Argentina" y "tiradas cortas" dejan de ser un texto y se ven. Una plancha, un corte y una pieza es la escasez explicada sin decirla.
- **El color asoma por la ranura del corte** (un trazo del color del modelo con un núcleo incandescente). El corte va revelando el color a medida que avanza.
- **La pieza cortada se transforma en la foto real**: el frente vectorial lleno de color se funde con el recorte fotográfico del modelo. El paso de pieza a producto queda en una sola transformación.
- **El tambor de pulido como drop**: es un paso real del acetato, y como objeto es una ruleta de colores que gira con el bombo.
- **El número de serie grabado con el láser**: ya no es un dato en una ficha ni un certificado. Se ve cómo se hace, y "N° 07/24" es **ilustrativo**.
- **El logo también sale de la máquina**: el cierre lo recorta el láser.
- **Sin precio**, como en todas las versiones.

## 4. Técnica

- **El recorrido del corte** es el contorno cat-eye vectorial de la marca (montura exterior + dos lentes) parametrizado por longitud de arco, así el cabezal avanza a velocidad constante y la ranura se dibuja hasta el punto exacto.
- **Chispas sin estado**: cada chispa nace en la posición que tenía el cabezal en su instante de emisión (recalculada desde `t`), sale con dirección y velocidad pseudoaleatorias, cae con gravedad y se apaga en 0,35 s. Se componen en modo `lighter`.
- **Arranque de tubo fluorescente**: la luz sigue una tabla de parpadeos (0,8 · 0,1 · 0,9 · 0,2 · 1) antes de quedar fija.
- **Grabado raster**: el texto aparece barrido de arriba abajo por una línea de escaneo, con el cabezal oscilando a lo ancho.
- **Luces del drop**: un `color` blend tiñe toda la nave con el acetato del modelo de cada negra.
- **Sincronía**: `music.py` exporta **117 eventos con nombre** (`lights`, `sheet`, `clamp`, `engrave`, `step`, `cut`, `flood`, `lift`, `word`, `drop`, `spin`, `serial`, `vline`, `yline`, `final`, `piece`, `cta`, `store`, `sign`, `sparkle`). La duración de cada corte en la imagen es la misma que la de su zumbido en el audio.
- **Motion blur real**: de 6 a 14 sub-frames con obturador de 180° (más en la entrada de planchas, el vuelo de las piezas y el tambor). Los tres cortes duros (negras 24, 32 y 40) no se mezclan.
- **Música (Fa menor, techno ácido)**:
  - **motor paso a paso**: cuadrada con micro-pasos y resonancia de chasis, afinada nota por nota, que es literalmente la melodía;
  - **láser**: *zaps* de ruido con un tono a 3,1 kHz y un zumbido con crepitación;
  - **taller**: mordazas (golpe metálico con 4 modos inarmónicos), tubos fluorescentes y el tambor de pulido (granos de ruido con el ritmo de rotación);
  - **línea ácida tipo 303**: sierra con filtro resonante, acentos y ligados;
  - bombo, palmas, hats y pad.

## 5. Lo que descarté

- **Una línea de montaje con cinta transportadora**: ya se usó una cinta en la versión persianas.
- **Personas trabajando en el taller**: sin caras, el protagonista es el oficio y el material.
- **Mostrar la máquina entera en perspectiva**: con vista cenital sobre la cama, la pieza y el corte se leen a cualquier tamaño de pantalla.
- **Teñir también el plano del número de serie**: en la primera prueba las luces del drop seguían violetas sobre la patilla y competían con el grabado. Limité el teñido al tambor.

## 6. Iteraciones

1. **Música v1**, verificada con el espectrograma y la forma de onda: el arranque es solo taller (tubos, mordazas, *zaps*), los motores tocan con altura reconocible entre los 3,3 y los 5,8 s, y el ácido entra en el drop.
2. **Imagen v1** (hoja de contactos de 80 frames):
   - el grabado "MIRÁ EL VERANO" casi no contrastaba con la plancha (lo oscurecí y le agregué un bisel claro);
   - la luz violeta del drop seguía en el plano de la patilla (la limité al tambor).
3. **Render final** y **revisión del MP4 codificado**: ffprobe, hoja de contactos del propio MP4, frames en los cortes y nivel de audio.

## 7. Reproducir

```bash
cd tupe6
python3 music.py build/music.wav     # audio + build/score.json
node render.js                       # build/tupe_fabrica_20s.mp4
```
(Los recortes en `assets/` salen de `tupe2/prep_assets.py`.)

## 8. Tiempo total

**≈ 21 minutos de reloj** (inicio 19:06 UTC, entrega 19:26 UTC).

- 2 min: concepto (la fábrica propia; el color está debajo del gris) y estructura.
- 2 min: techno ácido, sonidos de taller (motores, láser, mordazas, tubos, tambor) y partitura de eventos.
- 3 min: cortadora, planchas, corte parametrizado, chispas, tambor, patilla y cierre recortado.
- 1 min: hoja de contactos y ajustes (contraste del grabado, luces del drop).
- 14 min: render final (1200 frames con 6 a 14 sub-frames, 863 s) y revisión del MP4. Este documento lo escribí mientras el render corría.
