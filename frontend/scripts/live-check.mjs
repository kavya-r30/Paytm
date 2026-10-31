// Normal-mode check: every surface against the running API with a real session (no fixtures).
// A page fails on an uncaught error, a console error, a view that does not match its contract, an API
// response >= 400, a render error or an empty body; with --click it also presses every enabled button on
// each device screen and reports the same failures per click. Screenshots go to e2e-output/live/.
// Usage (API on :8000 with one seeded shop, web on :3000):
//   node scripts/live-check.mjs [--web http://localhost:3000] [--api http://localhost:8000] [--click] [--only bill,khata]
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
const API = arg('api', 'http://localhost:8000');
const ONLY = arg('only', '').split(',').filter(Boolean);
const CLICK = process.argv.includes('--click');
const OUT = join(ROOT, 'e2e-output', 'live');

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
  '/s/normal-kirana',
  '/stage',
  '/director',
].filter((p) => !ONLY.length || ONLY.some((o) => p.includes(o)));

async function session(surface) {
  const res = await fetch(`${API}/v1/director/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer dev-director' },
    body: JSON.stringify({ surface }),
  });
  if (!res.ok) throw new Error(`director/session ${surface}: ${res.status} ${await res.text()}`);
  return (await res.json()).token;
}

const failures = [];

function watch(page, errors) {
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message.split('\n')[0]}`));
  page.on('console', (m) => {
    const text = m.text();
    if (m.type() === 'error' && !/favicon|Download the React DevTools/.test(text))
      errors.push(`console: ${text.split('\n')[0].slice(0, 240)}`);
    if (/\[arth\].*does not match/.test(text)) errors.push(`contract: ${text.slice(0, 240)}`);
  });
  page.on('response', async (r) => {
    if (!r.url().startsWith(API) || r.status() < 400) return;
    let body = '';
    try {
      body = (await r.text()).slice(0, 200);
    } catch {
      // stream closed
    }
    errors.push(`api ${r.status()} ${r.request().method()} ${r.url().slice(API.length)} ${body}`);
  });
}

async function settle(page) {
  // live pages hold the SSE stream open, so idle is best-effort
  await page.waitForLoadState('networkidle', { timeout: 6000 }).catch(() => {});
  await page.waitForTimeout(800);
}

async function visit(context, path) {
  const page = await context.newPage();
  const errors = [];
  watch(page, errors);
  const t0 = Date.now();
  try {
    const res = await page.goto(`${WEB}${path}${path.includes('?') ? '&' : '?'}lang=en`, {
      waitUntil: 'load',
      timeout: 60000,
    });
    await settle(page);
    const text = (await page.locator('body').innerText()).trim();
    if (!res?.ok()) errors.push(`HTTP ${res?.status()}`);
    if (!text) errors.push('empty body');
    if (/Application error|Unhandled Runtime Error/.test(text)) errors.push('render error');
    if (path.startsWith('/device/') && /demo data/i.test(text)) errors.push('still in fixture mode');
    mkdirSync(OUT, { recursive: true });
    await page.screenshot({ path: join(OUT, `${path.replace(/^\//, '').replace(/[/?=&]/g, '_')}.png`) });
    if (CLICK && path.startsWith('/device/')) await clickAll(page, path, errors);
  } catch (e) {
    errors.push(String(e).split('\n')[0]);
  }
  const ms = Date.now() - t0;
  await page.close();
  const unique = [...new Set(errors)];
  console.log(
    `${unique.length ? 'FAIL' : 'ok  '} ${path} (${ms} ms)${unique.length ? `\n     ${unique.join('\n     ')}` : ''}`,
  );
  if (unique.length) failures.push(`${path}: ${unique.join(' | ')}`);
}

async function clickAll(page, path, errors) {
  const labels = await page
    .locator('button:visible:not([disabled])')
    .evaluateAll((els) =>
      els.map((e) => (e.getAttribute('aria-label') || e.innerText || '').trim()).filter(Boolean),
    );
  for (const label of [...new Set(labels)].slice(0, 25)) {
    if (/^(Pause all|Stop|Reset|Logout|Log out)$/i.test(label)) continue;
    const before = errors.length;
    try {
      await page.goto(`${WEB}${path}?lang=en`, { waitUntil: 'load' });
      await settle(page);
      const button = page.getByRole('button', { name: label, exact: true }).first();
      if (!(await button.count())) continue;
      await button.click({ timeout: 3000 });
      await page.waitForTimeout(1200);
    } catch (e) {
      errors.push(`click "${label}": ${String(e).split('\n')[0].slice(0, 160)}`);
    }
    for (let i = before; i < errors.length; i++)
      if (!errors[i].startsWith('click')) errors[i] = `click "${label}" → ${errors[i]}`;
  }
}

const device = await session('device');
const consoleToken = await session('console');
const browser = await chromium.launch();
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 960 } });
  await context.addInitScript(
    ([d, c]) => {
      localStorage.setItem('arth.session', d);
      localStorage.setItem('arth.session.console', c);
    },
    [device, consoleToken],
  );
  for (const path of SURFACES) await visit(context, path);
  await context.close();
} finally {
  await browser.close();
}
console.log(
  `\n${SURFACES.length - failures.length}/${SURFACES.length} surfaces clean · screenshots in ${OUT}`,
);
process.exit(failures.length ? 1 : 0);
