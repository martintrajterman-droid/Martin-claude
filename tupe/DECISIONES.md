# DECISIONES — Spot TUPÉ · Carla Di Sí (15 s · 1080×1920 · 60 fps)

**Entregable:** `tupe/tupe_carladisi.mp4`, H.264 High, 1080×1920, 60 fps, AAC estéreo a 48 kHz, 15,00 s.
**Regla:** todo sale de código. No usé imágenes ni vídeo generados, ni samples, ni skills. Las dos piezas que me pasaron sirvieron solo como **referencia de medida** para redibujar la marca en vectores. Ningún píxel de esas fotos aparece en el spot.

---

## 1. Idea

**"Mirá el verano en otro color."**

TUPÉ son anteojos cat-eye de acetato en dos colores: mandarina y lima. Toda la pieza se apoya en esa dualidad, en dos discos de color que terminan siendo dos lentes. El spot va de la forma más simple (un punto de color) al producto, después a la marca y cierra con la llamada a la acción. Cada golpe de la música es un acontecimiento en pantalla.

| Negras | Tiempo | Qué pasa | Golpe que lo dispara |
|---|---|---|---|
| 0–4 | 0,00–2,14 | Aparece un disco mandarina y luego uno lima. Una línea dibuja la montura alrededor, los discos se transforman en lentes y el acetato se llena desde el puente. Arriba se escribe la firma *Carla Di Sí* | *bloop* grave, *bloop* agudo, *whoosh*, palma + *pop* |
| 4–8 | 2,14–4,29 | **MIRÁ / EL / VERANO**: una palabra por golpe, mientras los anteojos rebotan con el bombo. En la palma, un brillo barre los lentes | bombo, bombo, bombo, palma |
| 8–12 | 4,29–6,43 | **EN OTRO / COLOR.**: con cada bombo, un barrido circular cambia todo el mundo: fondo papel ↔ tinta y anteojos mandarina ↔ lima. Al final se acelera a semicorcheas | bombo y marimba (los últimos cuatro, a semicorchea) |
| 12–16 | 6,43–8,57 | Producto en 3D sobre tinta: el par lima gira y se ven las patillas. Aparecen etiquetas (ACETATO TRASLÚCIDO, LENTE DEGRADÉ, CAT-EYE), cada una con su nota. Con el riser, la cámara entra en el lente | una nota de marimba por etiqueta, riser |
| 16–20 | 8,57–10,71 | **DROP**: el logo **TUPÉ** se arma pieza por pieza en corcheas (barra, T, U, asta de la P, panza de la P, cúpula de la É, pie de la É y el acento). El acento cae último con un destello | impacto y 8 notas ascendentes, una por pieza; *sparkle* |
| 20–24 | 10,71–12,86 | Latigazo vertical al *key visual* de la marca: par mandarina arriba, par lima abajo y la firma **escrita a mano** en el medio. La pluma avanza un tramo con cada nota | *whoosh*; 8 notas = 8 tramos de escritura |
| 24–28 | 12,86–15,00 | Cierre: los anteojos salen hacia arriba y hacia abajo, la firma baja a firmar y el logo vuelve a armarse. *encontrá* / **TUPÉ©** / *en carladisi.com/tupe*, con subrayado coral y un destello final | impacto + acorde, dos notas (una por línea), *sparkle* |

El cierre replica la pieza oficial "encontrá TUPÉ© en carladisi.com/tupe", y el bloque 20–24 replica la foto de producto: naranja arriba, lima abajo y la firma al medio. Las dos composiciones que me dieron aparecen en el spot, animadas.

## 2. Marca: redibujo fiel en vectores

No había SVG oficial, solo dos imágenes chicas (201×251 y 399×501). Por eso todo se midió **columna por columna** sobre los píxeles y después se verificó **superponiendo** el vector sobre la referencia ampliada (`build/check.png`).

- **TUPÉ**: lo reconstruí como geometría exacta, en unidades de 1 px de la referencia:
  - la barra fina de la T, que también tapa el brazo izquierdo de la U;
  - el asta de la T con terminación semicircular;
  - la U, con un contador estrecho de radio 3,6;
  - la P, que es un asta recta más un círculo completo (la muesca en V sale sola);
  - la É, que es una cúpula con una ranura vertical, un pie en cuarto de elipse y el acento en forma de píldora;
  - el ©.
  - Tras dos rondas de ajuste, el vector coincide con el original a menos de ~0,5 px de la referencia.
- **Firma "Carla Di Sí"**: la redibujé como **trazos en orden de escritura** y no como un contorno relleno. Son 7 gestos (C-a-r-l-a de un tirón, la D en tres trazos, la i, S+í y la tilde), suavizados con Catmull-Rom y con el grosor medido. Así se puede **escribir sola** con la pluma (*write-on*).
- **Anteojos**: medí el contorno exterior del par naranja (borde superior e inferior en cada columna) y el lente lo ajusté por superposición. Es simétrico por espejo. Los colores salen de muestrear la foto:
  - montura mandarina `#F8B414`, montura lima `#CEF104`;
  - lente del par mandarina: degradé de `#D9895E` a casi blanco;
  - lente del par lima: degradé ciruela, de `#3E2840` a gris;
  - coral de la firma `#E54F4E`; fondo `#FAF5F2`.
- El acetato traslúcido es un degradé vertical con borde interior más oscuro, bisagras que se ven a través del material, un brillo especular en la ceja y un reflejo que barre los lentes. Para el giro 3D, las patillas se proyectan en perspectiva.

## 3. Sincronía: una sola partitura

`music.py` no solo genera el audio: escribe `build/score.json` con **119 eventos con nombre** (`disc`, `fill`, `kick`, `clap`, `shake`, `note`, `callout`, `piece`, `stroke`, `whip`, `final`, `line`, `sparkle`…). La imagen lee esa misma lista, así que la sincronía es exacta por construcción y no "a ojo":

- Rebote y aplastamiento de los anteojos = `pulse("kick")`.
- Cada cambio de color = un evento `kick` o `note`.
- Cada pieza del logo **impacta exactamente en su corchea**. Acelera hacia el golpe y rebota después, nunca antes.
- La firma avanza un tramo por cada `stroke`.
- Los destellos sobre el acetato aparecen en los contratiempos del *shaker*.

Lo verifiqué renderizando frames justo antes, en y justo después de cada golpe clave (negras 0, 1, 3, 8, 9, 11, 11.25, 12, 16, 16.5, 19.5 y 24).

## 4. Música (sintetizada desde cero, numpy)

- **112 BPM en 4/4: 7 compases dan exactamente 15,000 s.** Es un *groove* soleado tipo nu-disco, en La mayor/Fa# menor: F#m9 · Dmaj9 · E6 · C#m7 · **Aadd9** (el drop resuelve "en casa") · F#m9 · Dmaj9 · Aadd9.
- **Instrumentos**, todos ecuaciones:
  - **bombo**: seno con barrido de tono;
  - **palmas**: ráfagas de ruido con paso banda;
  - **shaker**: ruido con paso alto y envolvente corta;
  - **bajo**: sub + sierra PolyBLEP filtrada;
  - **pad**: 5 sierras desafinadas por nota, en estéreo, con barrido de filtro;
  - **marimba**: FM 1:4 con índice que cae en ~25 ms, más la resonancia del tubo; es la voz melódica que "toca" cada evento visual;
  - **campana** FM 1:3,5;
  - ***bloops***: senos con glissando;
  - ***pop***, ***whoosh***, ***riser*** e **impactos**.
- **Mezcla**: *sidechain* calculado desde los eventos de bombo, reverb por convolución con una respuesta al impulso **sintética**, saturación suave y −1 dBFS. Al final hay un fundido de 350 ms.

## 5. Motion blur real, sin mezclar cortes

- Cada frame es una función pura de `t`. Promedio entre **6 y 40 sub-frames** dentro de un obturador de 180°.
- Uso más muestras donde el movimiento es más rápido: los barridos circulares (crecen ~1500 px en 0,2 s), el relleno del acetato, el latigazo vertical y el drop.
- **Los sub-frames nunca cruzan un corte duro.** El único corte duro es el drop (negra 16): el interior del lente pasa al fondo papel. Los sub-frames se recortan a su lado del corte, así que el primer frame del drop no tiene ni un poco del plano anterior.
- Las transiciones continuas (barridos, latigazo, zoom en el lente) sí llevan desenfoque, porque ahí el movimiento es real.

## 6. Lo que descarté

- **Usar los píxeles de la foto de producto** dentro del spot: el pedido era "solo código" y la foto mide 399 px. Redibujar los anteojos me permitió girarlos en 3D, cambiarles el color con cada golpe y dibujarlos con una línea.
- **Vectorizar la firma por contorno** (relleno): habría sido más "literal", pero no se puede escribir. La firma de una diseñadora tiene que verse trazada.
- **Copy largo o con especificaciones técnicas** (por ejemplo "UV400" o "polarizados"): no tengo datos del producto y no quise prometer nada falso. Las etiquetas solo nombran lo que se ve: acetato traslúcido, lente degradé, cat-eye.
- **Soles girando en órbita detrás del logo** (primera versión): ensuciaban la lectura de TUPÉ y el sol mandarina tapaba el acento, que también es mandarina. Los reemplacé por dos soles fijos que entran con muelle y laten con el bombo.
- **Fondo coral en la alternancia de color**: el lima sobre coral vibraba mal. La alternancia es papel ↔ tinta, que además hace brillar el lima.
- **Fundido a negro al final**: un anuncio tiene que terminar en la llamada a la acción legible. El último frame es el cierre completo.

## 7. Iteraciones

1. **Medición de marca**: mapas ASCII de las referencias y corridas de píxeles por fila para la firma (por canal de "rojez") y para el logo.
2. **Vectores v1 → v2** con superposición:
   - los bordes derecho e inferior del logo quedaban ~1 px cortos (ajusté la U, el asta y la panza de la P, la cúpula y la ranura de la É, y el ©);
   - el pie de la É estaba en el cuadrante equivocado;
   - el lente era ~6 % más grande que el real;
   - la base de la D y la panza de la S estaban ~1 px arriba;
   - los trazos eran demasiado gruesos (−14 %).
3. **Música v1 → v2**: en el espectrograma, el *whoosh* llegaba a 24 kHz (estridente) y el *sparkle* producía parciales con aliasing. Bajé el techo del filtro a 7 kHz y el *sparkle* una octava.
4. **Imagen v1** (hoja de contactos de 60 frames):
   - los anteojos ocupaban el 85 % del ancho y no respiraban (escala de 3,85 a 3,6);
   - los soles orbitando ensuciaban el logo;
   - la firma se cruzaba con el logo en el cierre: ahora baja con `outExpo` en 0,4 s y el logo arranca 0,1 s después.
5. **Imagen v2** (frames a ±2 de cada golpe): los barridos circulares dejaban **anillos** de motion blur con 14 muestras. Pasé a 40 muestras solo en los 0,16 s posteriores a cada barrido.
6. **Render final** y **revisión del MP4 codificado**: ffprobe (resolución, fps, cantidad de frames, duración y pistas), hoja de contactos extraída del propio MP4, frames de los cortes y nivel de audio.

## 8. Reproducir

```bash
cd tupe
python3 music.py build/music.wav     # audio + build/score.json (eventos)
node render.js --sheet               # hoja de contactos (opcional)
node render.js                       # build/tupe_carladisi.mp4
```

## 9. Tiempo total

**≈ 25 minutos de reloj** (inicio 13:44 UTC, entrega 14:06 UTC).

- 7 min: análisis de las referencias, medición píxel a píxel y redibujo vectorial de TUPÉ, de la firma y de los anteojos, con dos rondas de verificación por superposición.
- 4 min: composición y síntesis de la música más la partitura de eventos, con una corrección guiada por el espectrograma.
- 6 min: motor de escenas (7 bloques, transiciones y motion blur adaptativo).
- 2 min: revisión con hoja de contactos y frames alrededor de cada golpe, más dos correcciones.
- 6 min: render final (900 frames con 6 a 40 sub-frames, 366 s), revisión del MP4 y ajuste de headroom del AAC (el pico codificado llegaba a 0,0 dB; lo dejé en −1,5 dB). Este documento lo escribí mientras el render corría.
