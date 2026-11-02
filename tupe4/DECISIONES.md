# DECISIONES — TUPÉ · "Mirá el verano con otro color" · versión CIUDAD (20 s)

**Entregable:** `tupe4/tupe_ciudad_20s.mp4`, H.264 High, 1080×1920, 60 fps, AAC estéreo a 48 kHz, 20,000 s.
**Materiales:** los recortes de las fotos del PPT *TUPÉ · momento.02* (los cinco colores y el local) y los datos del brief. Todo lo demás es código: la ciudad dibujada en vectores, la tipografía, el logo y la firma redibujados, y la música sintetizada desde cero. No usé modelos de imagen, vídeo ni audio, ni samples.

---

## 1. Idea: el verano no es solo la playa

El pedido fue "que no parta desde la playa". Fui al otro verano, el que tiene la clienta de TUPÉ: **el verano en Buenos Aires**. Hay calor (34° en el cartel de la farmacia), cemento, un colectivo que pasa y bocinas, y todo gris. TUPÉ es de Carla, la óptica de autor de Buenos Aires, y el local está en Palermo Soho, así que la ciudad es su lugar natural.

**Dinámica nueva: un plano grúa vertical.** El formato 9:16 pide subir. La cámara sube un edificio porteño **un piso por golpe** y cada piso que llega **se inunda de color** desde el TUPÉ apoyado en su balcón. Arriba, en la terraza, la ciudad entera se pinta y los cinco colores quedan colgados del **tendedero**.

| | Playa (`tupe2`) | Persianas (`tupe3`) | **Ciudad (`tupe4`)** |
|---|---|---|---|
| Mundo | playa vectorial | playa en tiras | **calle, edificio, terraza y skyline porteño** |
| Movimiento | el lente se desplaza | tiras que se encastran y giran | **la cámara sube piso por piso y frena en cada golpe** |
| Entrada del color | ventana con forma de lente | giro 3D de cada tira | **inundación circular desde el TUPÉ de cada balcón** |
| Música | balear 96 BPM | pop surf 120 BPM | **cumbia digital 108 BPM** |
| Gesto sonoro | filtro que se abre | radio AM → hi-fi | **la cumbia del vecino se acerca piso por piso** |

## 2. Estructura (108 BPM · 9 compases = 36 negras = 20,000 s)

| Negras | Tiempo | Qué pasa | Golpe |
|---|---|---|---|
| 0–4 | 0–2,2 s | **Calle en gris**: vereda de baldosas, el local con la firma Carla Di Sí en la vidriera, un plátano y el cartel de farmacia, que pasa de 31° a 34°. Pasa un colectivo (el 152) | golpe de calor, bocina, colectivo con Doppler, salto del termómetro |
| 4–20 | 2,2–11,1 s | **La grúa sube 8 pisos**, uno cada dos negras. Cada piso llega en su golpe y se inunda de color desde el TUPÉ del balcón: violeta, caramelo, flúo, gris, nude, caramelo, violeta, flúo. En la otra ventana hay una escena de verano: ventilador girando, sandía, helado o una radio. **La radio del 8° es de donde sale la cumbia**. Placa de portero con el piso y una etiqueta "N° piso · modelo". Arriba: "MIRÁ / EL VERANO" → "CON OTRO / COLOR." | por piso: *pew* + *whoosh* de grúa; la cumbia sube un escalón de cercanía |
| 20–24 | 11,1–13,3 s | **DROP en la terraza**: el skyline se inunda de color en 5 franjas, una por corchea. "¡QUÉ TUPÉ!" Los cinco colores caen al tendedero, uno por corchea, y se balancean con broches | impacto; un golpe de timbal por cada par colgado |
| 24–28 | 13,3–15,6 s | La cámara se acerca a la soga: cada par tiene una **etiqueta colgante con su número de serie**. "N° de serie en la patilla" · "21–24 piezas por color." · "Hecho en Argentina · 100% acetato argentino" | un cencerro por etiqueta |
| 28–32 | 15,6–17,8 s | "Un anteojo que es tuyo / y de nadie más." **El viento se lleva cuatro pares**; queda el verde flúo y la cámara se acerca hasta él | ráfaga de viento, *pew* ascendente |
| 32–36 | 17,8–20 s | Cierre: TUPÉ© armado en semicorcheas, *encontrá* / *en carladisi.com/tupe*, la foto del local, "Probalos en Palermo Soho · Buenos Aires", firma y destello | impacto + acorde de acordeón, *sparkle* |

## 3. Decisiones

- **Arrancar en la vidriera de Carla**: el primer plano de la ciudad es el local con la firma en el vidrio. La marca está desde el frame 1, en gris, como todo.
- **Un piso por golpe y cada piso con un color**: los 8 pisos recorren la colección, y la placa de portero ("3°", "lab002 · verde flúo") lo hace legible sin explicar.
- **La radio del 8° piso**: la música tiene un origen en la imagen. Cuanto más subimos, más cerca está.
- **El tendedero** convierte la colección en algo casero, porteño y de verano: anteojos colgados como trajes de baño al sol. Las etiquetas colgantes con número de serie ("N° 03/22", "N° 07/24"…) muestran la tirada corta y la numeración. Los números son **ilustrativos** y respetan el dato del brief de 21 a 24 piezas por color.
- **"De nadie más" con el viento**: los otros cuatro vuelan y queda uno. Es la misma idea de exclusividad de las otras piezas, con una acción nueva.
- **Sin precio**, por el motivo del FODA del PPT ("precio alto sin relato").

## 4. Técnica

- **Mundo en coordenadas propias** (suelo en y=0, pisos hacia arriba) y una **cámara** que interpola entre destinos con `inOutExpo`. Cada movimiento termina 20 ms después del golpe, así que la frenada es el golpe.
- **Inundación de color**: cada piso se dibuja en gris y encima en color, recortado por un círculo que crece desde el TUPÉ del balcón (`outExpo` de 0,6 s). El skyline usa 5 franjas verticales que se llenan desde la base, una por corchea.
- **Paleta que se apaga**: toda la ciudad se dibuja con una función de color que, en modo gris, convierte cada tono a su luminancia comprimida. Lo que es gris y lo que es color es exactamente el mismo dibujo.
- **Sincronía**: `music.py` exporta **82 eventos con nombre** (`heat`, `bocina`, `bus`, `thermo`, `floor`, `word`, `drop`, `flood`, `hang`, `tag`, `vline`, `yline`, `unpin`, `zoom`, `final`, `piece`, `cta`, `sign`, `sparkle`) y la imagen se calcula desde ellos: el colectivo cruza con la duración exacta de su sonido, cada par cae al tendedero en su golpe de timbal, la radio late con el bombo.
- **Motion blur real**: de 6 a 20 sub-frames con obturador de 180° (más en las subidas de la grúa, la llegada a la terraza, el zoom final y el colectivo). El único corte duro es el del cierre, y el desenfoque no lo cruza.
- **Música (cumbia digital, La menor, cadencia andaluza Am–G–F–E)**:
  - **güira**: ráfaga de ruido modulada por los "dientes" del rallador, con patrón largo-corto;
  - **cencerro** estilo 808: dos cuadradas inarmónicas filtradas;
  - **timbal** con aro y resonancia; **bajo** en 1 y 3 con la quinta en el "y" del 2 y del 4;
  - **acordeón sintetizado**: dos lengüetas por nota desafinadas 6 cents (el *musette*), pulsos estrechos, fuelle y trémolo; acordes a contratiempo y melodía;
  - ***pews*** de cumbia digital.
- **La calle también es síntesis**: tránsito (ruido marrón filtrado y motor lejano), colectivo diésel con Doppler y bocina de dos tonos.
- **Mezcla**: la cumbia pasa por un filtro y una ganancia de "cercanía" que suben en 8 escalones, uno por piso, mientras la calle se va quedando abajo. En la terraza suena entera.

## 5. Lo que descarté

- **Otra variante de playa o de pileta como mundo principal**: el pedido era salir de la playa. La pileta de lona en la terraza queda como guiño, no como escenario.
- **Persianas o tiras en las ventanas**: hubieran repetido la gramática de la pieza anterior. Acá el color entra como una inundación desde el objeto.
- **Personas dibujadas en los balcones**: con un dibujo vectorial plano pueden verse genéricas o caricaturescas, y desvían la atención del producto. Los objetos (ventilador, sandía, helado, radio) cuentan el verano sin cara.
- **Un mapa o el Obelisco**: postal turística, no el verano cotidiano de la clienta.
- **La vista lateral del flúo**: ya se usó en las dos piezas anteriores. El número de serie ahora vive en etiquetas colgantes.

## 6. Iteraciones

1. **Música v1**, verificada con el espectrograma y la forma de onda: la cumbia empieza filtrada y baja, y se abre por escalones hasta los 11 s (la terraza).
2. **Imagen v1** (hoja de contactos de 80 frames):
   - la copa del árbol y el cartel de 34° tapaban las ventanas del 1° piso (los bajé, y el árbol toma color con el 1° piso);
   - los cinco pares del tendedero se tocaban (los separé y achiqué a 270 px);
   - el resaltador de "COLOR." tomaba el beige del piso "gris" y no se leía (pasé a verde flúo);
   - faltaba que los TUPÉ de los balcones reaccionaran al bombo y al timbal.
3. **Verificación puntual**: en la llegada a la terraza aparecían franjas negras a los costados. Agregué un fondo base y alargué los edificios vecinos hasta el techo.
4. **Render final** y **revisión del MP4 codificado**: ffprobe, hoja de contactos del propio MP4, frames del corte final y nivel de audio.

## 7. Reproducir

```bash
cd tupe4
python3 music.py build/music.wav     # audio + build/score.json
node render.js                       # build/tupe_ciudad_20s.mp4
```
(Los recortes en `assets/` salen de `tupe2/prep_assets.py`.)

## 8. Tiempo total

**≈ 17 minutos de reloj** (inicio 18:09 UTC, entrega 18:26 UTC).

- 2 min: concepto (el verano porteño) y dinámica (plano grúa piso por piso).
- 3 min: cumbia digital, sonido de calle y partitura de eventos.
- 4 min: la ciudad en vectores (calle, local, 8 pisos, terraza, tendedero, skyline) y la cámara.
- 2 min: hoja de contactos y dos rondas de correcciones (árbol, cartel, tendedero, resaltador, franjas negras).
- 10 min: render final (1200 frames con 6 a 20 sub-frames, 605 s) y revisión del MP4. Este documento lo escribí mientras el render corría.
