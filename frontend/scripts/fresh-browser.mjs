// What a person sees: a brand-new browser (no session, no injected token) opens the app and uses it.
// Logs every backend request and what the page shows, so "not connected" can be told apart from "broken".
// Usage: node scripts/fresh-browser.mjs [--stale]   (--stale starts with an expired/foreign token in storage)
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'e2e-output', 'fresh');
mkdirSync(OUT, { recursive: true });
const API = 'http://localhost:8000';
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1280, height: 960 } });
if (process.argv.includes('--stale'))
  await context.addInitScript(() => {
    if (!sessionStorage.getItem('seeded')) {
      localStorage.setItem('arth.session', 'expired.or.foreign.token');
      sessionStorage.setItem('seeded', '1');
    }
  });
const page = await context.newPage();
const log = [];
page.on('console', (m) => m.type() === 'error' && log.push(`console: ${m.text().slice(0, 160)}`));
page.on('pageerror', (e) => log.push(`pageerror: ${e.message.slice(0, 160)}`));
page.on('response', (r) => {
  if (r.url().startsWith(API) && !r.url().includes('/v1/stream'))
    log.push(`${r.request().method()} ${r.url().slice(API.length).split('?')[0]} -> ${r.status()}`);
});
const show = async (label) => {
  const mode = await page.evaluate(() =>
    localStorage.getItem('arth.session') ? 'live session' : 'NO SESSION',
  );
  const text = (await page.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 220);
  console.log(`\n== ${label} [${mode}] ${page.url()}\n   ${text}`);
  await page.screenshot({ path: join(OUT, `${label.replace(/\W+/g, '_')}.png`) });
};

await page.goto('http://localhost:3000/device/home', { waitUntil: 'load' });
await page.waitForTimeout(6000);
await show('home after first load');

for (const q of [
  'aaj kitna aaya',
  'Parle-G kitna bacha hai',
  'aaj kitne bill bane',
  'Priya ka khata kitna hai',
  'kaunsa maal khatam ho raha hai',
  'sabse zyada kya bika',
]) {
  const dock = page.getByPlaceholder(/Bolo ya likho|Speak or type/);
  await dock.fill(q);
  await dock.press('Enter');
  await page.waitForTimeout(6000);
  const said = await page
    .locator('text=/./')
    .evaluateAll(() => document.body.innerText.replace(/\s+/g, ' '))
    .catch(() => '');
  console.log(`\nASK "${q}"\n   ${String(said).slice(0, 400)}`);
  await page.screenshot({ path: join(OUT, `ask_${q.replace(/\W+/g, '_')}.png`) });
}
console.log(`\nBACKEND REQUESTS (${log.length}):\n${[...new Set(log)].join('\n')}`);
await browser.close();
