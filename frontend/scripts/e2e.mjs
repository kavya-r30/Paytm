// T7.18 Playwright E2E + screenshot matrix (run via `python dev.py e2e`, which starts the API and web servers).
// 1. Matrix: every device screen and every other surface × locales, in fixture mode (fresh browser, no session).
//    A page fails on an uncaught error, a failed render or an empty body. Screenshots go to e2e-output/.
// 2. Live: the Director plays a library scenario through the UI against the API; every beat must pass, then the
//    device opens on the shop the Director built.
// Usage: node scripts/e2e.mjs [--web http://localhost:3000] [--locales en,hi,ta,xx-LONG] [--scenario billing_smoke]
import { mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 ? process.argv[i + 1] : fallback;
};
const WEB = arg('web', 'http://localhost:3000');
const LOCALES = arg('locales', 'en,hi,ta,xx-LONG').split(',');
const SCENARIO = arg('scenario', 'billing_smoke');
const OUT = join(ROOT, 'e2e-output');

const registry = readFileSync(join(ROOT, 'screens/device/registry.ts'), 'utf8');
const DEVICE = [...registry.matchAll(/^ {2}([a-z]+): \w+\.\w+,$/gm)].map((m) => m[1]);
const CONSOLE = ['home', 'work', 'ask', 'plans', 'ledger', 'capital', 'r4', 'trust', 'settings'];
const SURFACES = [
  ...DEVICE.map((s) => `/device/${s}`),
  ...CONSOLE.map((s) => `/console/${s}`),
  '/device-voice',
  '/customer-display',
  '/phone/owner',
  '/phone/priya',
  '/stage',
  '/director',
];

const failures = [];

async function visit(context, path, locale) {
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  try {
    const sep = path.includes('?') ? '&' : '?';
    const res = await page.goto(`${WEB}${path}${sep}lang=${encodeURIComponent(locale)}`, {
      waitUntil: 'networkidle',
      timeout: 60000,
    });
    const text = (await page.locator('body').innerText()).trim();
    if (!res?.ok()) errors.push(`HTTP ${res?.status()}`);
    if (!text) errors.push('empty body');
    if (/Application error|Unhandled Runtime Error/.test(text)) errors.push('render error');
    const dir = join(OUT, locale);
    mkdirSync(dir, { recursive: true });
    await page.screenshot({ path: join(dir, `${path.replace(/^\//, '').replace(/[/?=&]/g, '_')}.png`) });
  } catch (e) {
    errors.push(String(e).split('\n')[0]);
  }
  await page.close();
  if (errors.length) failures.push(`${locale} ${path}: ${errors.join('; ')}`);
  return errors.length === 0;
}

async function matrix(browser) {
  for (const locale of LOCALES) {
    const context = await browser.newContext({ viewport: { width: 1280, height: 960 } });
    let ok = 0;
    for (const path of SURFACES) ok += (await visit(context, path, locale)) ? 1 : 0;
    console.log(`matrix ${locale}: ${ok}/${SURFACES.length}`);
    await context.close();
  }
}

async function live(browser) {
  const context = await browser.newContext({ viewport: { width: 430, height: 1400 } });
  const page = await context.newPage();
  page.on('pageerror', (e) => failures.push(`director: ${e.message}`));
  await page.goto(`${WEB}/director?lang=en`);
  await page.waitForFunction(() => document.querySelectorAll('select option').length > 5, null, {
    timeout: 60000,
  });
  await page.selectOption('select', SCENARIO);
  await page.getByRole('button', { name: /Play this scenario/ }).click();
  await page.waitForSelector('text=Ready:', { timeout: 180000 });
  const beats = await page.locator('main button:has-text(" · ")').count();
  for (let i = 0; i < beats; i++) {
    const before = await page.locator('ul li').count();
    await page.getByRole('button', { name: /Next beat/ }).click();
    await page.waitForFunction((n) => document.querySelectorAll('ul li').length > n, before, {
      timeout: 120000,
    });
  }
  const log = await page.locator('ul li').allInnerTexts();
  const results = log.filter((l) => / → /.test(l));
  const passed = results.filter((l) => / → pass/.test(l)).length;
  console.log(`live ${SCENARIO}: ${passed}/${beats} beats pass`);
  if (passed !== beats)
    failures.push(`live ${SCENARIO}: ${results.filter((l) => !/ → pass/.test(l)).join(' | ')}`);
  mkdirSync(OUT, { recursive: true });
  await page.screenshot({ path: join(OUT, `director-${SCENARIO}.png`), fullPage: true });
  const device = await context.newPage();
  await device.setViewportSize({ width: 1280, height: 960 });
  // live pages hold the SSE stream open, so wait for the screen itself rather than network idle
  await device.goto(`${WEB}/device/home?lang=en`, { waitUntil: 'load' });
  await device.waitForTimeout(4000);
  if (await device.locator('text=demo data').count()) failures.push('live: device still in fixture mode');
  await device.screenshot({ path: join(OUT, 'device-live-home.png') });
  await context.close();
}

const browser = await chromium.launch();
try {
  if (!process.argv.includes('--live-only')) await matrix(browser);
  if (!process.argv.includes('--matrix-only')) await live(browser);
} finally {
  await browser.close();
}
if (failures.length) {
  console.log(`\nE2E FAILED (${failures.length}):\n${failures.map((f) => `  ${f}`).join('\n')}`);
  process.exit(1);
}
console.log(`E2E GREEN · screenshots in ${OUT}`);
