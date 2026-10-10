// Renderiza scene.html frame a frame con Chromium headless y lo entuba a ffmpeg.
// Uso:
//   node render.js                      -> build/tupe_carladisi.mp4 (vídeo + audio)
//   node render.js --frames 0,120,450   -> PNGs sueltos en build/preview/
//   node render.js --sheet              -> hoja de contactos (1 frame cada 0.25 s)
const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const BUILD = path.join(ROOT, "build");
const FPS = 60, TOTAL = 15 * FPS;
const args = process.argv.slice(2);
const WORKERS = parseInt(process.env.WORKERS || "3", 10);

async function makePage(browser, audio) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("console", m => console.log("[page]", m.text()));
  page.on("pageerror", e => { console.error("[pageerror]", e); process.exit(1); });
  await page.goto("file://" + path.join(ROOT, "scene.html"));
  await page.evaluate(a => window.init(a), audio);
  await page.waitForFunction(() => window.READY === true);
  return page;
}

async function frame(page, f) {
  await page.evaluate(f => window.renderFrame(f), f);
  return page.locator("#c").screenshot({ type: "png" });
}

(async () => {
  const audio = JSON.parse(fs.readFileSync(path.join(BUILD, "score.json"), "utf8"));
  const browser = await chromium.launch({ args: ["--disable-gpu-vsync", "--font-render-hinting=none"] });

  const fi = args.indexOf("--frames");
  if (fi >= 0 || args.includes("--sheet")) {
    const list = fi >= 0 ? args[fi + 1].split(",").map(Number)
      : Array.from({ length: 60 }, (_, i) => Math.round(i * 15));
    const out = path.join(BUILD, "preview");
    fs.mkdirSync(out, { recursive: true });
    const pages = await Promise.all(Array.from({ length: Math.min(WORKERS, list.length) }, () => makePage(browser, audio)));
    let next = 0;
    await Promise.all(pages.map(async p => {
      while (next < list.length) {
        const f = list[next++];
        fs.writeFileSync(path.join(out, `f${String(f).padStart(4, "0")}.png`), await frame(p, f));
      }
    }));
    await browser.close();
    console.log("preview ok", list.length);
    return;
  }

  const outFile = path.join(BUILD, "tupe_carladisi.mp4");
  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
    "-i", path.join(BUILD, "music.wav"),
    "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-tune", "animation",
    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
    "-x264-params", "keyint=60:min-keyint=60",
    "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
    "-movflags", "+faststart", "-shortest", outFile,
  ], { stdio: ["pipe", "inherit", "inherit"] });

  const pages = await Promise.all(Array.from({ length: WORKERS }, () => makePage(browser, audio)));
  const done = new Map();
  let next = 0, written = 0;
  const t0 = Date.now();
  const flush = async () => {
    while (done.has(written)) {
      const buf = done.get(written); done.delete(written);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
      written++;
      if (written % 60 === 0) {
        const el = (Date.now() - t0) / 1000;
        console.log(`frame ${written}/${TOTAL}  ${el.toFixed(0)}s  ~${(el / written * (TOTAL - written)).toFixed(0)}s restantes`);
      }
    }
  };
  let flushing = Promise.resolve();
  await Promise.all(pages.map(async p => {
    while (next < TOTAL) {
      const f = next++;
      // no adelantarse demasiado al escritor (memoria acotada)
      while (f - written > 40) await new Promise(r => setTimeout(r, 20));
      done.set(f, await frame(p, f));
      flushing = flushing.then(flush);
    }
  }));
  await flushing;
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
  console.log("listo:", outFile, ((Date.now() - t0) / 1000).toFixed(0) + "s");
})();
