# DECISIONES — Showreel de motion design (15 s · 1920×1080 · 60 fps)

**Entregable:** `showreel/showreel.mp4`, H.264 High, 1920×1080, 60 fps, AAC estéreo a 48 kHz, 15,00 s.
**Regla que me impuse:** todo sale de código. No hay imágenes, vídeos, samples ni modelos generativos. Cada píxel lo dibuja `scene.html` (Canvas 2D) y cada muestra de audio la calcula `music.py` (numpy).

---

## 1. La idea

Un reel de motion designer no se trata de "efectos bonitos". Lo que tiene que mostrar es **criterio**: ritmo, tipografía, transiciones que tengan sentido y un sistema visual coherente. Por eso planteé el reel como un recorrido por las disciplinas del oficio. Cada compás de la música es un capítulo:

| Compás | Tiempo | Capítulo | Qué demuestra |
|---|---|---|---|
| 1 | 0,00 – 1,875 | **00 IGNITION**: un punto late con el bombo y arma una retícula técnica de arcos, regla y coordenadas; al final se estira en una línea | Anticipación, *squash & stretch*, construcción desde lo mínimo |
| 2 | 1,875 – 3,75 | **01 KINETIC TYPE**: la línea corta la pantalla y se abre. "MOTION" sube letra a letra con muelles escalonados, se aplasta con el bombo y alterna TYPE / FORM / TIME / RHYTHM en semicorcheas (wght 100 ↔ 900) | Tipografía cinética, *stagger*, sincronía con la música |
| 3 | 3,75 – 5,625 | **02 FORM**: zoom ×34 *a través del hueco de la O*. Dentro hay una cuadrícula de 45 formas que se transforman (círculo → cuadrado → triángulo → cruz → estrella) en una onda que sale del centro | *Match cut*, *morphing*, sistemas y retículas |
| 4 | 5,625 – 7,5 | **03 PARTICLES**: zoom dentro del cuadrado cobalto central. 6.000 partículas forman "DESIGN" y, durante el redoble, colapsan en un vórtice hasta quedar en un punto | Simulación, composición, tensión antes del drop |
| 5 | 7,5 – 9,375 | **04 DEPTH (el drop)**: flash, temblor de cámara y aberración cromática. Túnel 3D con un icosaedro sombreado a mano y etiquetas técnicas enganchadas a sus vértices | 3D, cámara, impacto |
| 6 | 9,375 – 11,25 | **05 SYSTEMS**: corte con glitch a un mosaico de 8 piezas: *easing*, *squash & stretch*, espectro de audio **real**, peso tipográfico, nube de puntos 3D, ilusión óptica, fase y contador de frames | Amplitud técnica, como en un reel de "breakdowns" |
| 7 | 11,25 – 13,125 | **06 LIQUID**: el mosaico se parte en dos y aparece un líquido (metaballs) con el manifiesto "EVERY FRAME ON PURPOSE.". El texto cambia de color al quedar dentro del líquido, que crece hasta llenar la pantalla | Formas orgánicas, máscaras, mensaje |
| 8 | 13,125 – 15,00 | **07 SIGNATURE**: el naranja que llena la pantalla se contrae hasta ser el círculo del logo. Encajan el cuadrado y el triángulo, el nombre entra cerrando el tracking y el subtítulo se escribe a máquina. Fundido a negro | Cierre de marca y *payoff* |

Los tres elementos del logo (círculo, cuadrado y triángulo) son las mismas formas de la escena 02, y el círculo es literalmente el líquido de la escena 06 que se contrae. El final retoma lo que se vio antes.

## 2. Decisiones clave

### Música primero, imagen después
- **128 BPM en 4/4: 8 compases dan exactamente 15,000 s.** Elegí el tempo para que la duración pedida coincidiera con una frase musical completa. Así cada escena dura un compás y cada corte cae en un tiempo fuerte.
- La música se compone y se renderiza **antes** que la imagen. `music.py` exporta además `music_analysis.json` con las envolventes por frame (bombo, palmas, hats, bajo, campana, FX) y un espectro de 24 bandas. La imagen reacciona **al audio real**: el punto late con el bombo, las letras se aplastan con él, la cuadrícula hace un *ripple* retardado por distancia, el panel 03 muestra el espectro de verdad y el fondo de partículas se ilumina con el redoble.
- Estructura: intro con riser → *groove* (bombo, hats, bajo a contratiempo, arpegio) → redoble y silencio de una negra → **drop** en 7,5 s con impacto, supersaw y una melodía de campana FM → segundo riser → impacto final y cola de reverb.
- Armonía en fa menor: Fm9 · D♭maj9 · A♭(add9) · E♭, y se resuelve en Fm9.

### Síntesis 100 % desde cero (sin un solo sample)
- **Bombo**: seno con barrido exponencial de tono de 236 a 46 Hz, un *click* de ruido y saturación tanh.
- **Palmas**: tres microráfagas de ruido más una cola, pasadas por un filtro paso banda.
- **Hi-hats**: seis ondas cuadradas inarmónicas (la receta de la 808) más ruido, con paso alto.
- **Bajo**: dos sierras PolyBLEP (sin aliasing) más una sub-octava senoidal y un filtro con envolvente.
- **Pad**: *supersaw* de 7 voces desafinadas por nota, abiertas en estéreo, con barrido de filtro.
- **Arpegio**: *pluck* de cuadrada + sierra con filtro percusivo, en *ping-pong* estéreo.
- **Campana**: síntesis FM con relación 1:3,5 e índice que decae.
- **FX**: risers (ruido con paso banda ascendente más un tono que sube), impactos (sub con caída de tono más ráfaga filtrada) y un *downlifter*.
- **Filtros**: SVF TPT de Zavalishin, estable aunque el corte cambie en cada muestra.
- **Reverb**: convolución FFT con una respuesta al impulso **sintética** (ruido con decaimiento exponencial que se oscurece con el tiempo y pre-delay).
- **Mezcla**: *sidechain* calculado desde los tiempos del bombo, saturación suave en el bus y normalizado a −1 dBFS, con fundido de 250 ms al final.

### Motor visual: cada frame es una función pura de `t`
- No hay estado acumulado ni simulación paso a paso. La posición de cada partícula, de cada forma y de cada letra se calcula directamente a partir del tiempo. Esto me da tres ventajas:
  1. **Motion blur real**: cada frame promedia de 4 a 16 sub-frames dentro de un obturador de ~200°. En los zooms ×30 subo a 16 muestras para que no aparezcan "fantasmas" escalonados.
  2. **Render en paralelo**: 4 pestañas de Chromium renderizan frames salteados, y un reordenador los manda en orden a ffmpeg.
  3. Puedo saltar a cualquier frame para revisarlo sin recalcular lo anterior.
- El motion blur **no atraviesa los cortes duros** (el drop y el glitch): los sub-frames se recortan contra la lista de cortes. En la primera versión el flash del drop salía lavanda porque mezclaba el cobalto anterior con el blanco.
- Todo el *easing* está escrito a mano: expo, cubic, quint, back, elastic y un **muelle amortiguado analítico** (`1 − e^(−ζωt)·cos(ω√(1−ζ²)t)`) para las letras.
- **Morphing sin correspondencia de vértices**: todas las formas son estrelladas desde su centro, así que las describo como radios r(θ) muestreados en los mismos 240 ángulos (intersección rayo-polígono). Transformar una forma en otra es interpolar radios, sin saltos ni vértices que se crucen.
- **El hueco de la O**: mido el contador de la O de Inter Display Black escaneando píxeles. Dibujo la escena siguiente dentro de una elipse algo más grande que el hueco y después vuelvo a pintar la O encima. Así el portal sigue el contorno exacto del glifo.
- **Metaballs**: campo Σr²/d² a media resolución. El borde se antialiasa dividiendo (f−1) por el gradiente, es decir, con una distancia con signo aproximada. El resultado es un borde de 1 px sin importar cómo se fundan las bolas.
- **3D sin librerías**: proyección en perspectiva, rotaciones a mano, descarte de caras traseras, orden del pintor e iluminación Lambert con tres tonos.
- **Post**: aberración cromática radial (separo canales con `multiply` y los recompongo con `lighter`), glitch de franjas determinista, grano animado (6 texturas de ruido con desplazamiento aleatorio por frame) y viñeta.
- **HUD** de "monitor de edición", dibujado encima del motion blur para que quede nítido: timecode a 60 fps, capítulo con efecto de decodificación, indicador de negras y compás, y barra de progreso. Le da al reel un lenguaje de herramienta profesional y además ayuda a leer la estructura.

### Sistema visual
- **Paleta** reducida a 5 tintas: tinta `#0C0C10`, papel `#F1ECE2`, naranja `#FF4F1A`, cobalto `#2440FF` y ácido `#D7FF3D` (este último solo como acento). Cada capítulo cambia de fondo para que el cambio de sección se note sin texto.
- **Tipografía**: Inter Display en sus 9 pesos (del Thin al Black) para los titulares y DejaVu Sans Mono para las anotaciones técnicas. El contraste entre un grotesk enorme y un mono diminuto es un recurso clásico del diseño suizo y técnico.
- Las anotaciones ("spring(ω=20, ζ=.38)", "Σ r²/d² > 1", "6 000 particles · 0 keyframes") son un guiño: es un reel de alguien que **programa** el movimiento.

## 3. Lo que descarté

- **WebGL / shaders**: tenían más potencia (bloom, *raymarching*), pero Chromium headless en este contenedor no tiene GPU y el render por software de WebGL es frágil. Canvas 2D me daba control total, antialias de calidad y determinismo. El "wow" lo saqué de la coreografía y no de los shaders.
- **Python + PIL para la imagen**: no tiene antialias de vectores, el texto es pobre y no hay modos de fusión. Lo descarté a los pocos minutos.
- **Una simulación de partículas con estado**: rompía el motion blur por sub-frames y el render en paralelo. La reemplacé por posiciones analíticas (órbita → objetivo → vórtice).
- **Un monograma o un nombre inventado**: firmo como "CLAUDE", porque el reel es mío.
- **Metaballs con `filter: blur + contrast`**: el truco CSS clásico era lento a 1080p y dejaba bordes sucios. Calcular el campo directamente es más rápido y más limpio.
- **Más de 3 colores de acento y degradados**: le restaban identidad. Me quedé con tintas planas.
- **Melodía en el groove**: competía con la tipografía. La campana FM entra solo en el drop para que el momento crezca.
- **Exportar los frames a PNG en disco**: eran ~2,7 GB. Los mando por tubería directamente a ffmpeg.

## 4. Iteraciones

1. **Música v1**: el filtro Chamberlin SVF se volvía inestable con cortes altos y Q baja, y producía NaN y overflow. Lo reemplacé por un **SVF TPT (Zavalishin)**, que es estable por construcción.
2. **Música v2**: en el espectrograma (renderizado con ffmpeg para "escuchar con los ojos") la campana FM llenaba los agudos de parciales inarmónicos hasta 15 kHz. Bajé el índice de modulación de 4 a 2,2 y le di una caída más rápida.
3. **Imagen v1**, primera hoja de contactos (un frame cada 0,25 s):
   - El botón "click to play" del modo navegador aparecía en todos los frames, porque el CSS `display:flex` le ganaba al atributo `hidden`. Lo corregí.
   - Los metaballs se veían borrosos (smoothstep sobre un campo a 1/4 de resolución). Lo resolví con el borde normalizado por gradiente a 1/2 de resolución.
   - El flash del drop salía lavanda porque el motion blur mezclaba frames de antes y después del corte. Los sub-frames ya no cruzan cortes.
   - El icosaedro se veía marrón y apagado: el producto escalar de la luz tenía el signo invertido.
   - Las etiquetas 3D se superponían. Ahora están fijas en pantalla y la línea guía va hasta el vértice.
   - "DESIGN" en partículas se leía débil. Pasé de 4.096 a 6.000 partículas, más grandes y con un muestreo más denso.
   - La viñeta ensuciaba los fondos papel. La bajé de 0,42 a 0,26.
4. **Imagen v2**, frame a frame en cada transición:
   - Con 4 sub-frames, los zooms ×30 mostraban copias escalonadas. Pasé a un **motion blur adaptativo** de hasta 16 sub-frames en los tramos rápidos.
   - La aberración cromática dejaba un borde amarillo, porque el canal azul escalado hacia abajo no cubría el borde. Ahora todos los canales escalan ≥ 1.
   - El HUD desaparecía durante la apertura de la línea (tinta sobre tinta). Ahora cambia de color hasta que se abre la pantalla.
   - El mosaico tardaba en llenarse. Las piezas ahora entran cada 1/6 de negra.
   - Moví las anotaciones de la cuadrícula a los espacios entre filas porque chocaban con el HUD.
5. **Render final** y verificación con ffprobe (resolución, fps, duración y pistas) y con una hoja de contactos del MP4 ya codificado.

## 5. Cómo reproducirlo

```bash
cd showreel
python3 music.py build/music.wav          # música + build/music_analysis.json
node render.js --sheet                    # (opcional) hoja de contactos en build/preview
node render.js                            # build/showreel.mp4
```
Requisitos: Python 3 + numpy, Node + Playwright (Chromium), ffmpeg con libx264 y las fuentes Inter Display y DejaVu Sans Mono instaladas.
`scene.html` también se puede abrir en un navegador (sirviendo la carpeta por HTTP) para verlo en tiempo real con la música.

## 6. Tiempo total

**≈ 27 minutos de reloj** (inicio 23:55 UTC, entrega 00:19 UTC). Reparto aproximado:

- 5 min: concepto, storyboard por compases y composición y síntesis de la música (más 2 iteraciones guiadas por el espectrograma).
- 9 min: motor visual (8 escenas, transiciones, post y HUD).
- 4 min: revisión con hojas de contactos y frame a frame en cada transición, más 2 rondas de correcciones.
- 8,5 min: render final (900 frames con entre 4 y 16 sub-frames cada uno, 4 pestañas de Chromium en paralelo, 508 s) y codificación.
- 1 min: verificación con ffprobe y redacción de este documento (escrito mientras el render corría).
