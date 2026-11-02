# DECISIONES — TUPÉ · "Mirá el verano con otro color" · versión REVELADO (20 s)

**Entregable:** `tupe5/tupe_revelado_20s.mp4`, H.264 High, 1080×1920, 60 fps, AAC estéreo a 48 kHz, 20,000 s.
**Materiales:** los recortes de las fotos del PPT *TUPÉ · momento.02* (los cinco colores y el local) y los datos del brief. Todo lo demás es código: la cámara, la mesa, las viñetas de verano, el estuche, el paño, la limonada y el certificado son vectores. La música se sintetizó desde cero. No usé modelos de imagen, vídeo ni audio, ni samples.

---

## 1. Idea: el gris que se vuelve color, literalmente

La foto instantánea es la metáfora perfecta del concepto: **sale gris y se revela a color**. La pieza ya no parte de un lugar (playa o ciudad) sino de un **objeto y un gesto**: una cámara instantánea dispara con flash sobre una mesa en blanco y negro. Cada foto que expulsa se revela y muestra **un verano distinto con un TUPÉ adentro**:

| Foto | Verano | Modelo |
|---|---|---|
| 1 | atardecer sobre los techos | lab002 caramelo |
| 2 | pileta vista desde arriba, con cáusticas | lab002 verde flúo |
| 3 | paletas heladas | lab001 violeta |
| 4 | hojas de monstera | lab002 gris |
| 5 | santa rita en la pared | lab001 nude |

Ninguna es una playa: el verano está en muchos lugares.

**Dinámica nueva: stop-motion de mesa (flat-lay cenital).** Las fotos salen de la ranura, vuelan en arco y caen en la mesa en el golpe. En el drop, la **mesa misma toma color**: se vuelve un mantel al sol, con sombras de hojas que se mueven.

| | Playa | Persianas | Ciudad | **Revelado** |
|---|---|---|---|---|
| Punto de partida | playa | playa en tiras | calle | **sala oscura + flash** |
| Mecanismo del color | lente-ventana | giro de tiras | inundación por piso | **revelado químico de la foto** |
| Plano | mundo frontal | mosaico | grúa vertical | **cenital sobre una mesa** |
| Música | balear | surf | cumbia | **disco-funk 132 BPM** |
| Gesto sonoro | filtro | radio → hi-fi | se acerca | **cada foto revelada suma un instrumento** |

## 2. Estructura (132 BPM · 11 compases = 44 negras = 20,000 s)

| Negras | Tiempo | Qué pasa | Golpe |
|---|---|---|---|
| 0–2 | 0–0,9 s | Oscuridad. Solo brilla la ventana del flash cargando | silbido de carga del flash |
| 2–4 | 0,9–1,8 s | **FLASH**: aparece la mesa gris con la cámara. Primer disparo: la foto sale de la ranura | estallido del flash, obturador, motorcito |
| 4–8 | 1,8–3,6 s | La foto 1 cae en la mesa en el golpe y se revela: emulsión pizarra → manchas → imagen. "MIRÁ / EL VERANO" | bombo suave, obturador en 2 y 4, avance de película |
| 8–16 | 3,6–7,3 s | Fotos 2, 3, 4 y 5, cada vez más seguidas. "CON OTRO / COLOR." con resaltador flúo. **Cada foto revelada agrega un instrumento**: bajo (negra 8), clavinet (12), cuerdas (15) | disparo + expulsión por foto |
| 16–20 | 7,3–9,1 s | **Ráfaga de flashes** en corcheas que fuerzan el revelado, más el riser | obturador + flash por corchea |
| 20–26 | 9,1–11,8 s | **DROP · "¡QUÉ TUPÉ!"**: la mesa se vuelve un mantel al sol con sombras de hojas, la cámara sale de cuadro y las fotos se van a los bordes como marco. Los cinco TUPÉ reales caen al centro en corcheas. Llegan el **estuche** (con la firma), el **paño** y una limonada | impacto, vientos, palmas, hats abiertos |
| 26–30 | 11,8–13,6 s | **Certificado de serie**: "N° 07/24", y se sellan "21–24 piezas por color", "N° de serie en la patilla · lab002 verde flúo" y "Diseño Carla Di Sí · Hecho en Argentina · 100% acetato argentino · estuche y paño" | un clic de sello por línea |
| 30–34 | 13,6–15,5 s | "Un anteojo que es tuyo / y de nadie más." En el golpe, los otros cuatro **se des-revelan a gris** y queda el verde flúo | flash suave |
| 34–44 | 15,5–20 s | **El cierre es una foto que se revela**: flash, la foto entra, la emulsión se aclara y aparece *encontrá* / **TUPÉ©** / *en carladisi.com/tupe*. Carla **firma la foto en el borde blanco**. La foto del local cae encima ("probalos en Palermo Soho") y hay un destello final | disparo + impacto + acorde, notas de clavinet para el CTA, *sparkle* |

## 3. Decisiones

- **Revelado químico creíble**: la foto sale de un pizarra oscuro (`#3C4A4E`) que se aclara mientras manchas de emulsión se disuelven. La imagen aparece debajo y el pie de foto se escribe al final.
- **Los flashes de la ráfaga revelan**: dramatizan el build-up y adelantan el color que llega en el drop.
- **Flat-lay del drop con objetos del brief**: el *reason why* del PPT incluye "estuche y paño", y aparecen como objetos reales sobre la mesa. El estuche lleva la firma de Carla.
- **Certificado de serie** en lugar de contador o cartel: el número de serie como **documento**, que es lo que se le entrega a quien compra algo único. "N° 07/24" es **ilustrativo**.
- **"De nadie más" con un des-revelado**: los otros cuatro pierden el color y vuelven al gris de la emulsión. Es la misma metáfora, en reversa.
- **El cierre es una foto firmada**: el logo se revela como una foto más y Carla la firma en el borde. Es la "diseñadora visible" del FODA, en un gesto.
- **Sin precio**, como en las otras versiones.

## 4. Técnica

- **Viñetas animadas dentro de cada foto** (392 × 392): las cáusticas de la pileta se mueven, el sol del atardecer late, las hojas se mecen y las flores tiemblan. Los pares flotan sobre la pileta con su sombra.
- **Sombras de contacto reales**: cada recorte genera su propia silueta desenfocada (`blur + brightness(0)`) para la sombra del flat-lay.
- **Luz de verano**: una textura de sombras de hojas desenfocadas, generada una vez y aplicada en `multiply` con un vaivén lento.
- **Sincronía**: `music.py` exporta **102 eventos con nombre** (`whine`, `flash`, `shot`, `land`, `developed`, `snap`, `burst`, `drop`, `place`, `obj`, `cert`, `stamp`, `yline`, `choose`, `endshot`, `enddev`, `cta`, `store`, `caption`, `sign`, `sparkle`). Cada foto cae exactamente en la negra siguiente a su disparo y cada línea del certificado se sella con su clic.
- **Motion blur real**: de 6 a 16 sub-frames con obturador de 180° (más en los arcos de las fotos, las caídas del flat-lay, el drop y la foto final). El único corte duro es el del cierre, tapado por el flash, y el desenfoque no lo cruza.
- **Música (disco-funk, Re dórico Dm9 ↔ G13, se resuelve en Fa 6/9)**:
  - **percusión de cámara**, toda síntesis: obturador (dos clics del espejo y un golpe), avance de película (trinquete), carga del flash (seno de 900 Hz a 7,5 kHz), estallido del flash y motorcito de expulsión;
  - **bajo** de octavas, **clavinet** (cuerda Karplus-Strong + filtro de pastilla tipo wah);
  - **cuerdas** (5 sierras por nota), **vientos** (sierra + cuadrada con envolvente de filtro), palmas y hats.
- **Arreglo como gesto**: antes del primer revelado solo suena la cámara. El bajo entra con la foto 1 revelada, el clavinet con la 2, las cuerdas con la 4 y la banda completa con vientos en el drop.

## 5. Lo que descarté

- **Otra vez un lugar como punto de partida**: el pedido era alejarse de la playa. Elegí partir de un objeto (la cámara) para que el verano pueda estar en cualquier lado.
- **Personas en las fotos**: sin caras, el verano se cuenta con objetos y texturas, y el protagonista es siempre el TUPÉ.
- **Stop-motion a 12 fps** (salteando cuadros): era tentador por el estilo, pero chocaba con el motion blur real que pide la pieza. Lo dejé fluido a 60 fps.
- **Una marca de cámara reconocible**: es una cámara instantánea genérica, sin logos.
- **La vista lateral del flúo**: ya se usó dos veces. El número de serie ahora es un certificado.

## 6. Iteraciones

1. **Música v1**, verificada con el espectrograma y la forma de onda: el bombo de la parte "en blanco y negro" competía con la cámara, así que lo bajé de 0,55 a 0,32 hasta que entra el bajo.
2. **Imagen v1** (hoja de contactos de 80 frames):
   - "MIRÁ EL VERANO" pisaba la primera foto (subí el texto y bajé las posiciones de las fotos 80 px);
   - "¡QUÉ TUPÉ!" tapaba el primer par del flat-lay (bajé la columna de pares 100 px y los achiqué a 520 px).
3. **Render final** y **revisión del MP4 codificado**: ffprobe, hoja de contactos del propio MP4, frames del corte final y nivel de audio.

## 7. Reproducir

```bash
cd tupe5
python3 music.py build/music.wav     # audio + build/score.json
node render.js                       # build/tupe_revelado_20s.mp4
```
(Los recortes en `assets/` salen de `tupe2/prep_assets.py`.)

## 8. Tiempo total

**≈ 20 minutos de reloj** (inicio 18:30 UTC, entrega 18:49 UTC).

- 2 min: concepto (la foto instantánea como metáfora del gris → color) y dinámica cenital.
- 3 min: disco-funk, percusión de cámara y partitura de eventos.
- 3 min: cámara, mesa, revelado químico, 5 viñetas de verano, flat-lay, certificado y cierre en foto.
- 1 min: hoja de contactos y una ronda de ajustes de composición.
- 13 min: render final (1200 frames con 6 a 16 sub-frames, 755 s) y revisión del MP4. Este documento lo escribí mientras el render corría.
