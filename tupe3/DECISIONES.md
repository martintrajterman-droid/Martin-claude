# DECISIONES — TUPÉ · "Mirá el verano con otro color" · versión PERSIANAS (20 s)

**Entregable:** `tupe3/tupe_persianas_20s.mp4`, H.264 High, 1080×1920, 60 fps, AAC estéreo a 48 kHz, 20,000 s.
**Materiales:** las mismas fotos del PPT *TUPÉ · momento.02* (recortadas en la pieza anterior) y los datos del brief. Todo lo demás es código. La música es nueva y está sintetizada desde cero. No usé modelos de imagen, vídeo ni audio, ni samples.

---

## 1. Misma idea, otra dinámica

El concepto no cambia: **el verano en gris, que se ve de otro color con un TUPÉ**. Cambia la forma de contarlo.

| | Pieza anterior (`tupe2`) | Esta pieza (`tupe3`) |
|---|---|---|
| Gramática | **ventana**: el lente se mueve sobre un mundo gris | **persiana**: la pantalla se corta en 5 tiras, una por color |
| Movimiento | continuo, fluido, de cámara | **por cortes y encastres**: tiras que se desalinean, se alinean, giran y frenan en seco |
| Cómo entra el color | a través del lente | cada tira **gira en 3D** y del otro lado está en color |
| Drop | el mundo entero en color | **color-blocking**: seis cortes duros a fondos planos, uno por golpe |
| Número de serie | contador | **cartel split-flap** estilo aeropuerto |
| Cierre | aparece sobre papel | **bajan persianas de papel** y el local también gira al color, tira por tira |
| Música | balear, 96 BPM, steel pan | **pop surf**, 120 BPM, guitarra Karplus-Strong, órgano, batería |
| Gesto sonoro | filtro que se abre gradualmente | **radio AM → hi-fi** en 5 escalones, uno por tira que gira |

## 2. Estructura (120 BPM · 10 compases = 40 negras = 20,000 s)

| Negras | Tiempo | Qué pasa | Golpe |
|---|---|---|---|
| 0–4 | 0–2 s | Verano gris; el sol sube. Cuatro líneas cortan la pantalla en 5 tiras, una por corchea. Las tiras se desalinean (chk) y vuelven a encastrar | bombo, 4 ticks, chk, chk |
| 4–8 | 2–4 s | "MIRÁ / EL / VERANO", una palabra por golpe. Cada palabra **desalinea las tiras**, que vuelven con rebote. En el 7, un glitch más fuerte | chk por palabra, glitch en la palma |
| 8–12 | 4–6 s | El texto cambia a "CON OTRO COLOR." y las tiras **giran una a una al color** en corcheas (del centro hacia afuera). Cada tira es un color de la colección con su par y su etiqueta | 5 *fwip* + 5 notas de guitarra; la radio sube un escalón por giro |
| 12–16 | 6–8 s | **Cinta transportadora**: cada tira desliza su par en sentidos alternados y frena exacto en cada golpe; el verano corre detrás en paralaje | riff surf de guitarra |
| 16–20 | 8–10 s | **Barajado**: los colores rotan entre tiras en corcheas con giros rápidos, riser y **colapso** de las cinco tiras a una línea | *fwip* + nota por giro |
| 20–24 | 10–12 s | **DROP · "¡QUÉ TUPÉ!"**: seis cortes duros de color-blocking (flúo, violeta, caramelo, gris, nude, flúo), cada uno con su par girando a escena y su etiqueta. El texto cambia a tinta o papel según el fondo | impacto + nota de guitarra por corte; pandereta |
| 24–28 | 12–14 s | Estudio: vista lateral del flúo y **split-flap** que baraja letras hasta clavar "N°07/24", celda por celda. Se marca la patilla grabada. "N° de serie en la patilla" · "21–24 piezas por color." · "Hecho en Argentina · 100% acetato argentino" | ráfaga de clics del cartel, nota de llegada |
| 28–32 | 14–16 s | **Macro del acetato** en 5 tiras (el ala cat-eye de cada color). "Un anteojo que es tuyo / y de nadie más." En la palma, cuatro tiras giran a gris y queda solo el verde flúo, marcado en coral | *fwip* + palma |
| 32–40 | 16–20 s | **Bajan 5 persianas de papel** en semicorcheas y aparece el cierre: TUPÉ© armado pieza por pieza, *encontrá* / *en carladisi.com/tupe*. El local de Palermo Soho entra en gris y **gira al color tira por tira**. "Probalos en Palermo Soho", firma Carla Di Sí y destello final | 5 *fwip*, impacto, 2 notas del CTA, 5 notas ascendentes, *sparkle* |

## 3. Decisiones clave

- **Las cinco tiras son los cinco colores.** La división de la pantalla no es arbitraria: 1920 / 5 = 384 px por tira, y el orden (violeta, caramelo, flúo, gris, nude) es la colección completa.
- **Los giros van del centro hacia afuera** (tira 3, 2, 4, 1, 5): el color nace en el centro de la pantalla y se expande.
- **La cinta frena *en* el golpe**: cada desplazamiento es un `inOutExpo` que termina 20 ms después del golpe. El ojo lee la frenada como el golpe.
- **Corte duro en el drop**, a propósito: después de 8 s de giros y deslizamientos continuos, el color-blocking necesita el contraste de lo seco. El motion blur se recorta en cada corte (son 8 cortes en total, incluidos el split-flap y el macro), así que ningún frame mezcla dos planos.
- **Contraste del texto según el fondo**: tinta sobre flúo, caramelo y gris; papel sobre violeta y nude.
- **Split-flap**: cada celda baraja caracteres cada 45 ms con la solapa superior cayendo y frena en escalera (85 ms entre celdas). Así el número de serie se convierte en un objeto mecánico y coleccionable. "N° 07/24" es ilustrativo, no un número real.
- **Macro del acetato**: en una pieza main sobre valor, ver el material de cerca (el canto del ala, la bisagra a través del acetato traslúcido) dice "objeto premium" mejor que cualquier texto.
- **Sin precio**, igual que en la pieza anterior y por el mismo motivo del FODA: "precio alto sin relato".

## 4. Técnica

- **Persiana 3D**: cada tira se dibuja con escala vertical `|cos θ|` y sombra según el ángulo. Muestra la cara gris hasta los 90° y la de color después. Las caras son lienzos completos (verano gris con texto / verano color + tinte + par) que se recortan por tira, así el desalineado horizontal es solo un desplazamiento del recorte.
- **Sincronía**: `music.py` exporta **120 eventos con nombre** (`line`, `shift`, `align`, `word`, `glitch`, `textswap`, `flip`, `riff`, `shuffle`, `collapse`, `cut`, `flap`, `flap_land`, `vline`, `yline`, `choose`, `slat`, `piece`, `cta`, `pflip`, `sparkle`…) y la imagen se calcula desde ellos.
- **Motion blur adaptativo**: de 6 a 36 sub-frames con un obturador de 180°. La cinta transportadora recorre 1500 px en ~0,24 s: con 12 muestras dejaba copias escalonadas del par y con 36 queda un desenfoque continuo.
- **Música**:
  - **Karplus-Strong** (ruido en una línea de retardo que se promedia a sí misma) para la guitarra surf, con posición de púa y brillo, y para el bajo;
  - trémolo de 7,5 Hz en la guitarra;
  - **reverb de resorte** sintética (ruido con dispersión en chirp y rebotes);
  - **órgano aditivo** de 5 drawbars con leslie a contratiempo;
  - caja, hats, pandereta y palmas sintetizadas;
  - FX propios: *chk* (deslizamiento), *fwip* (giro de persiana) y la ráfaga de clics del split-flap.
- **Radio AM**: la mezcla completa pasa por una banda de 350–2800 Hz, en mono, saturada y con crujidos, y se hace un crossfade a la versión hi-fi en 5 escalones (uno por giro de tira) hasta el 100 % en el drop.

## 5. Lo que descarté

- **Repetir el lente-ventana con otro montaje**: el pedido era otra dinámica, no otra edición. Por eso cambié la gramática entera (tiras), no solo el orden.
- **Tiras verticales**: en 9:16 dan bandas de 216 px de ancho, donde un anteojo no entra. Las horizontales (1080 × 384) alojan un par completo por tira.
- **Barridos o fundidos en el drop**: blandos después de tanto movimiento continuo; corte duro.
- **Un contador numérico como en la pieza anterior**: el split-flap es más táctil y es otra dinámica.
- **Persianas en el cierre con fundido**: las persianas de papel bajan girando, coherentes con el resto de la pieza.

## 6. Iteraciones

1. **Música v1**, verificada con el espectrograma y la forma de onda: la parte de radio quedaba demasiado baja frente al hi-fi (subí su nivel ×1,3). El crossfade en escalones se ve en el espectrograma entre los 4,5 y los 10 s.
2. **Imagen v1** (hoja de contactos de 80 frames):
   - "¡QUÉ TUPÉ!" salía cortado a la izquierda, porque un `textAlign = center` heredado desplazaba el texto fuera de su máscara;
   - la cinta transportadora mostraba el par duplicado en copias escalonadas: pasé a 36 sub-frames solo en esas ventanas.
3. **Verificación puntual** de la cinta (frames 383–445) y del primer frame del drop.
4. **Render final** y **revisión del MP4 codificado**: ffprobe, hoja de contactos extraída del propio MP4, frames a ambos lados de cada corte y nivel de audio.

## 7. Reproducir

```bash
cd tupe3
python3 music.py build/music.wav     # audio + build/score.json
node render.js                       # build/tupe_persianas_20s.mp4
```
(Los recortes en `assets/` salen de `tupe2/prep_assets.py`.)

## 8. Tiempo total

**≈ 16 minutos de reloj** (inicio 17:51 UTC, entrega 18:06 UTC).

- 2 min: concepto de la nueva dinámica y comparación con la pieza anterior.
- 3 min: música (Karplus-Strong, órgano, batería, resorte, radio AM → hi-fi) y partitura de eventos.
- 3 min: sistema de persianas, color-blocking, split-flap, macro y cierre.
- 1 min: hoja de contactos y dos correcciones (texto del drop y blur de la cinta).
- 9 min: render final (1200 frames con 6 a 36 sub-frames, 546 s) y revisión del MP4. Este documento lo escribí mientras el render corría.
