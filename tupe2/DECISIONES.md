# DECISIONES — TUPÉ · "Mirá el verano con otro color" (pieza main, 20 s)

**Entregable:** `tupe2/tupe_main_20s.mp4`, H.264 High, 1080×1920, 60 fps, AAC estéreo a 48 kHz, 20,000 s.
**Materiales:** las fotos de producto y del local salen del PPT *TUPÉ · momento.02* (6 fotos de producto y 1 del local de Palermo Soho), igual que los datos del brief. Todo lo demás es código: el mundo de verano en vectores, la tipografía, el logo y la firma redibujados, y la música sintetizada desde cero. No usé modelos de imagen, vídeo ni audio, ni samples.

---

## 1. Idea

**El verano está en gris. Solo a través de un TUPÉ se ve en color, y cada color de la colección lo tiñe distinto.**

Es literal y es la promesa del brief a la vez: un anteojo raro y exclusivo cambia cómo ves el verano. Lo distinto de esta pieza frente al spot anterior es que **el lente funciona como filtro**: es una ventana con la forma exacta del lente real (extraída de la foto), a través de la cual el mundo recupera el color. Los colores de la colección dejan de ser una lista: cada uno es una forma de mirar.

El audio hace lo mismo: el verano gris **suena** gris (mono, filtrado a ~400 Hz) y la mezcla se abre en brillo y en estéreo cada vez que aparece color.

## 2. Estructura (96 BPM · 8 compases = 32 negras = 20,000 s)

| Negras | Tiempo | Bloque | Qué pasa | Golpe |
|---|---|---|---|---|
| 0–4 | 0,0–2,5 | **Verano apagado** | Playa vectorial en gris (sol, nubes, mar, velero, sombrilla, pelota). El sol sube un escalón por negra. Aparece "VERANO" | latido sordo por negra, tick, ola |
| 4–8 | 2,5–5,0 | **Mirá el verano** | El **lab002 caramelo** cae y aterriza en el golpe; a través de sus lentes el sol sale naranja. Salta de un destino a otro, uno por golpe: mar, sombrilla, centro. "MIRÁ / EL / VERANO", una palabra por golpe | bombo + steel pan en cada movimiento |
| 8–12 | 5,0–7,5 | **Con otro color** | Entra el **verde flúo** y el mundo a través del lente se vuelve frío y neón. "CON / OTRO / COLOR.", con un resaltador del color del acetato | steel pan + silbido |
| 12–16 | 7,5–10,0 | **Carrusel** | En corcheas: violeta, gris, nude, caramelo, flúo… Cada modelo tiñe el verano con su color y muestra su etiqueta (lab001 · violeta, etc.). Con el riser, la cámara **entra en el lente** | 8 notas de steel pan, redoble de congas, riser |
| 16–20 | 10,0–12,5 | **DROP · "¡QUÉ TUPÉ!"** | Ya estamos del otro lado del lente: **todo el verano en color**. "¡QUÉ" / "TUPÉ!" en dos golpes, "[ lab.002 ] sin reglas, sin ley." y los cinco colores caen a tomar sol, uno por corchea | impacto, apertura total de la mezcla |
| 20–24 | 12,5–15,0 | **Número de serie** | Corte a estudio: vista lateral del flúo con "lab002" grabado en la patilla, marcado en coral, "N° de serie en la patilla". Un contador sube 01 → 24 en semicorcheas y aterriza en "21–24 piezas por color." · "Hecho en Argentina · 100% acetato argentino" | ticks en semicorcheas, golpe de llegada |
| 24–28 | 15,0–17,5 | **Tuyo y de nadie más** | Los cinco colores entran apilados, uno por corchea. En el golpe, cuatro **se apagan a gris** y salen de cuadro; el flúo queda solo y crece. "Un anteojo que es tuyo / y de nadie más." y un sello coral "N° 07/24" | notas por modelo, golpe "choose", tick del sello |
| 28–32 | 17,5–20,0 | **Cierre** | El logo TUPÉ© se arma en semicorcheas, *encontrá* / *en carladisi.com/tupe* con subrayado. La foto del **local de Palermo Soho** aparece en gris y se pinta de color con el destello final. "Probalos en Palermo Soho" y la firma Carla Di Sí escrita a mano | impacto + acorde, dos notas para el CTA, *sparkle* |

El cierre retoma el concepto: el local, que es donde se prueba un TUPÉ, también pasa de gris a color.

## 3. Rescate del PPT

- **Fotos**: los cinco frentes (lab001 violeta, lab002 caramelo, lab002 verde flúo, lab002 gris, lab001 nude), la vista lateral con el grabado "lab002" y el local.
- **Datos que usé**, todos tomados del brief:
  - "¡Qué tupé!" como remate;
  - "[ lab.002 ] = sin reglas, sin ley";
  - "Un anteojo que es tuyo y de nadie más";
  - N° de serie en la patilla;
  - 21–24 piezas por color;
  - Hecho en Argentina y 100% acetato argentino;
  - el local de Palermo Soho para la prueba.
- **Dirección estratégica**: el brief pide subir el ticket, comunicar escasez y deseo de colección y llegar a un público más atrevido. Por eso la segunda mitad deja de hablar del verano y pasa a hablar de **valor** (número de serie, tirada corta, hecho acá) y de **exclusividad** ("de nadie más").
- **No mostré precios.** En una pieza de deseo premium, el precio sin relato juega en contra; el propio FODA del PPT dice "precio alto sin relato". Tampoco inventé especificaciones técnicas.
- **"N° 07/24" es ilustrativo**: muestra cómo se ve la numeración, no un número real de serie.

## 4. Decisiones técnicas

### Recorte de producto y extracción del lente
`prep_assets.py` (numpy + PIL):
1. **Fondo**: crecimiento de regiones desde el borde sobre el blanco puro de estudio. Se suman los huecos blancos encerrados (el ojo de cerradura sobre el puente del lab002) y se descartan las motas chicas con apertura morfológica.
2. **Lente**: un criterio de color distinto por acetato, porque cada uno se relaciona de otra forma con su lente. El violeta se separa por saturación, el gris por el tono marrón del lente, el nude porque el lente es más azul que rojo. Desde semillas en el centro de cada lente la región crece y después se regulariza con su **envolvente convexa**, que tapa las patillas que se ven a través y los reflejos que el color no separa.
3. **Mate** suavizado y **descontaminación del borde blanco**, sin halo.
4. Salidas: montura sin lente, lente solo, versión completa, versión en gris y metadatos (cajas de los lentes y color medio del acetato).

### El lente como ventana
Por cada sub-frame:
1. Dibujo el verano dos veces: en gris como fondo y en color en una capa aparte, magnificada un 5 % alrededor del anteojo como haría una lente real.
2. Tiño la capa de color con el color del modelo (overlay).
3. La recorto con el **alfa exacto del lente de la foto** (`destination-in`).
4. Encima pongo el lente original al 26 % (conserva el degradé, los reflejos y las patillas), un brillo que barre el lente en cada golpe y, al final, la montura.

El resultado parece una foto de producto real mirando un mundo gráfico.

### Sincronía
`music.py` exporta **130 eventos con nombre** (`sun`, `glasses`, `move`, `swap`, `drop`, `rain`, `count`, `choose`, `stamp`, `piece`, `cta`, `sparkle`…) y la imagen lee esa misma lista:
- cada movimiento llega a su destino **justo en el golpe** (acelera hacia el beat);
- cada cambio de modelo es una nota del carrusel;
- el contador avanza un número por semicorchea;
- la firma y el logo se construyen sobre sus semicorcheas.

### Motion blur real
- Promedio de 6 a 18 sub-frames con un obturador de 180°. Uso más muestras en los aterrizajes, los cambios de modelo, el zoom al lente y la lluvia de anteojos.
- **Ningún sub-frame cruza un corte duro**. Hay tres cortes (negras 20, 24 y 28) y en ellos el primer frame de cada plano sale limpio.

### Música (numpy, desde cero)
- **96 BPM en Mi mayor**: Emaj9 · C#m7 · Amaj9 · B6 · **Eadd9** (el drop resuelve en la tónica) · C#m7 · Amaj9 · Eadd9.
- **Instrumentos**, todos ecuaciones:
  - **steel pan**: parciales 1 · 2 · 2,98, FM en el golpe y una leve caída de afinación;
  - **congas**: seno con barrido + ruido de golpe, versiones abierta y slap;
  - **shaker**, **bajo** (sub + sierra filtrada), **pad** de 5 sierras por nota;
  - **silbido**: seno con vibrato progresivo, portamento y "aire" de ruido filtrado en la nota;
  - **olas**: ruido filtrado que sube y rompe;
  - impactos y riser.
- **El gesto clave**: un filtro maestro de 380 Hz a 20 kHz y un ancho estéreo de 0 a 1 que siguen la curva de color de la imagen. Valen 0 en el verano gris, se abren a ~55 % cuando caen los anteojos, suben con cada modelo y llegan a 100 % en el drop.
- **Master** a −1,5 dBFS para dejar margen al AAC; la vez anterior el AAC tocó 0 dB.

## 5. Lo que descarté

- **Usar las fotos tal cual, con su fondo blanco**: la gracia es que el anteojo **real** mire un mundo y lo cambie. Sin recorte no hay ventana.
- **Teñir el mundo con `ctx.filter`** (grayscale/hue-rotate): era lento a 1080×1920 por sub-frame y menos controlable. Dibujo el mundo con una paleta que se convierte a gris de forma explícita.
- **Recorte de lentes solo por color**: en el violeta y el nude las patillas visibles detrás del lente y los reflejos dejaban agujeros y bordes mordidos. Lo reemplacé por la envolvente convexa del lente.
- **Escribir el copy dentro del mundo**, para que solo se lea a través del lente: era más poético, pero el copy dejaba de leerse en la mitad de los frames. Una pieza main tiene que comunicar, así que el texto va encima, nítido.
- **"COLOR." pintado del color del modelo**: el flúo sobre el cielo gris claro no se leía. Ahora va en tinta sobre un resaltador del color real del acetato (medido en la foto).
- **Precio y "solo 24 unidades" como urgencia de venta**: el brief habla de deseo de colección, no de liquidación. Usé "21–24 piezas por color" como dato de valor.
- **16:9**: el brief dice que hoy TUPÉ vive en Reels de @carladisi, así que la pieza main nace vertical. Las zonas seguras dejan el texto entre ~300 y ~1650 px.

## 6. Iteraciones

1. **Lectura del PPT**: texto de las 9 diapositivas y las 7 imágenes, y mapeo de cada foto a su modelo.
2. **Recortes v1**: los fondos salieron bien, pero los lentes del violeta y el nude tenían huecos por las patillas y los reflejos. En la **v2** apliqué la envolvente convexa por lente y la verifiqué sobre un fondo cian, donde se ven en el acto los errores de mate y de lente.
3. **Música v1**, verificada con el espectrograma: la parte gris queda contenida bajo ~2 kHz, se abre en 2,5 s y llega al espectro completo en 10 s.
4. **Imagen v1** (hoja de contactos de 80 frames):
   - "MIRÁ EL" y "VERANO" se pisaban;
   - "COLOR." en flúo era ilegible;
   - "¡QUÉ TUPÉ!" en blanco se perdía sobre el cielo claro (ahora lleva una sombra sólida en tinta y está más arriba);
   - la punta grabada de la patilla quedaba al borde del cuadro (achiqué y centré la vista lateral);
   - en "de nadie más", los anteojos apagados tapaban el texto: ahora se apagan en 0,18 s y salen de cuadro.
5. **Render final** y **revisión del MP4 codificado**: ffprobe, hoja de contactos extraída del MP4, frames en los cortes y nivel del audio.

## 7. Reproducir

```bash
cd tupe2
python3 -I prep_assets.py <carpeta con las imágenes del PPT> assets   # recortes + lentes
python3 music.py build/music.wav                                      # audio + build/score.json
node render.js                                                        # build/tupe_main_20s.mp4
```

## 8. Tiempo total

**≈ 20 minutos de reloj** (inicio 17:29 UTC, entrega 17:48 UTC).

- 3 min: lectura del PPT (texto de las 9 diapositivas y las 7 imágenes) y concepto.
- 3 min: recorte de producto y extracción de lentes, con dos versiones verificadas sobre fondo cian.
- 3 min: música y partitura de eventos, verificadas con el espectrograma.
- 5 min: mundo vectorial, efecto lente-ventana y las 6 escenas.
- 2 min: hoja de contactos, frames clave y una ronda de correcciones de legibilidad y composición.
- 8 min: render final (1200 frames con 6 a 18 sub-frames, 474 s) y revisión del MP4. Este documento lo escribí mientras el render corría.
