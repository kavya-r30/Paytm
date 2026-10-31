// Presenter walk-through after `python dev.py demo`: a fresh browser opens the Director (it must pick up the
// restored shop by itself), presses Next beat N times, then opens the stage. Logs every backend call.
// Usage: node scripts/demo-walk.mjs [beats=4] [--headed]
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'e2e-output', 'demo-walk');
mkdirSync(OUT, { recursive: true });
const WEB = 'http://localhost:3000';
const API = 'http://localhost:8000';
const beats = Number(process.argv.find((a) => /^\d+$/.test(a)) ?? 4);
const browser = await chromium.launch({ headless: !process.argv.includes('--headed') });
const context = await browser.newContext({ viewport: { width: 430, height: 1300 } });
const page = await context.newPage();
const calls = [];
page.on('response', (r) => {
  if (r.url().startsWith(API) && !/stream|healthz/.test(r.url()) && r.request().method() !== 'OPTIONS')
    calls.push(`${r.request().method()} ${r.url().slice(API.length).split('?')[0]} -> ${r.status()}`);
});
await page.goto(`${WEB}/director?lang=en`, { waitUntil: 'load' });
await page.waitForTimeout(5000);
const log = async () => (await page.locator('ul li').allInnerTexts()).slice(0, 6).join('\n   ');
console.log(`Director opened. Log:\n   ${await log()}`);
for (let i = 0; i < beats; i++) {
  await page.getByRole('button', { name: /Next beat/ }).click();
  await page.waitForTimeout(4000);
}
console.log(`\nAfter ${beats} x Next beat. Log:\n   ${await log()}`);
await page.screenshot({ path: join(OUT, 'director.png'), fullPage: true });
const stage = await context.newPage();
await stage.setViewportSize({ width: 1600, height: 900 });
await stage.goto(`${WEB}/stage?lang=en`, { waitUntil: 'load' });
await stage.waitForTimeout(8000);
await stage.screenshot({ path: join(OUT, 'stage.png') });
console.log(`\nStage: ${(await stage.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 200)}`);
console.log(`\nBackend calls:\n   ${[...new Set(calls)].join('\n   ')}`);
console.log(`\nscreenshots: ${OUT}`);
await browser.close();
