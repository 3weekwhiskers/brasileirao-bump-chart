// Render dist/index.html round by round into frames/ (then run encode_video.sh).
// Requires: npm i playwright  (and its Chromium).  Usage: node scripts/capture_video.mjs
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { mkdirSync, rmSync } from 'fs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const framesDir = resolve(root, 'frames');
rmSync(framesDir, { recursive: true, force: true });
mkdirSync(framesDir, { recursive: true });

const PER = 15;            // frames captured per round (the ~0.7s bar transition)
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1180, height: 1000 }, deviceScaleFactor: 1.25 });
await page.goto('file://' + resolve(root, 'dist/index.html'));
await page.addStyleTag({ content: '.controls{display:none!important}.wrap{padding-top:16px}' });
await page.waitForTimeout(300);

const R = await page.evaluate(() => DATA.R);
let f = 0;
const shot = async () => page.screenshot({ path: `${framesDir}/f${String(f++).padStart(4, '0')}.png` });
for (let r = 1; r <= R; r++) {
  await page.evaluate(v => window.__setRound(v), r);
  for (let k = 0; k < PER; k++) { await page.waitForTimeout(45); await shot(); }
}
for (let k = 0; k < 40; k++) await shot();   // hold final frame
await browser.close();
console.log(`Captured ${f} frames into frames/`);
