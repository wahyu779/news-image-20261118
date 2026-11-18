// main.ts — entry program for news-image-20261118, worldtoday-v2 layout.
// Copies the pre-rendered front page (entry.png, drawn by render.py
// from page.html with headless Chromium) into the output directory
// the harness provides. Node 22, standard library only, no network,
// no clock, no randomness: the same input bytes always produce the
// same output bytes.
const fs = require("node:fs");
const path = require("node:path");

function main() {
  const outDir =
    process.env.MAKEFUN_OUTPUT_DIR || path.join(process.cwd(), "out");
  const src = path.join(__dirname, "entry.png");
  const dst = path.join(outDir, "entry.png");
  fs.mkdirSync(outDir, { recursive: true });
  const data = fs.readFileSync(src);
  fs.writeFileSync(dst, data);
}

main();
