// Normal-mode UI flow: drives the device the way an owner does (taps, chips, buttons, the ask dock) against
// the running API, records every request the page sends to the backend, and checks the backend state after.
// Usage (API :8000 with one seeded shop, web :3000): node scripts/ui-flow.mjs [--headed]
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const WEB = 'http://localhost:3000';
const API = 'http://localhost:8000';
const OUT = join(ROOT, 'e2e-output', 'ui-flow');
mkdirSync(OUT, { recursive: true });

async function session(surface) {
  const res = await fetch(`${API}/v1/director/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer dev-director' },
    body: JSON.stringify({ surface }),
  });
  if (!res.ok) throw new Error(`session ${res.status}`);
  return (await res.json()).token;
}
const token = await session('device');
const api = async (path) => {
  const res = await fetch(`${API}${path}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`GET ${path} ${res.status}`);
  return res.json();
};

const log = []; // every backend request the UI made
const results = [];
const browser = await chromium.launch({ headless: !process.argv.includes('--headed') });
const context = await browser.newContext({ viewport: { width: 1280, height: 960 } });
await context.addInitScript((t) => localStorage.setItem('arth.session', t), token);
const page = await context.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(e.message.split('\n')[0]));
page.on('response', async (r) => {
  if (!r.url().startsWith(API) || r.url().includes('/v1/stream')) return;
  const req = r.request();
  let type = '';
  try {
    type = JSON.parse(req.postData() ?? '{}').type ?? '';
  } catch {
    // not JSON
  }
  let body = '';
  if (r.status() >= 400) body = (await r.text().catch(() => '')).slice(0, 160);
  log.push({
    method: req.method(),
    path: r.url().slice(API.length).split('?')[0],
    type,
    status: r.status(),
    body,
  });
});

async function step(name, fn) {
  const from = log.length;
  const errs = errors.length;
  try {
    await fn();
    const bad = log.slice(from).filter((l) => l.status >= 400);
    if (bad.length)
      throw new Error(bad.map((b) => `${b.method} ${b.path} ${b.type} ${b.status} ${b.body}`).join(' | '));
    if (errors.length > errs) throw new Error(errors.slice(errs).join(' | '));
    results.push(`ok    ${name}`);
  } catch (e) {
    results.push(`FAIL  ${name}: ${String(e.message ?? e).slice(0, 400)}`);
  }
  const posts = log.slice(from).filter((l) => l.method !== 'GET');
  results.push(...posts.map((l) => `        ${l.method} ${l.path} ${l.type} -> ${l.status}`));
  await page.screenshot({ path: join(OUT, `${name.replace(/[^a-z0-9]+/gi, '_').slice(0, 50)}.png`) });
}
const go = async (path) => {
  await page.goto(`${WEB}${path}${path.includes('?') ? '&' : '?'}lang=en`, { waitUntil: 'load' });
  await page.waitForTimeout(1500);
};
const until = async (fn, ms = 20000) => {
  const end = Date.now() + ms;
  for (;;) {
    if (await fn()) return;
    if (Date.now() > end) throw new Error('timed out waiting for the backend state');
    await page.waitForTimeout(700);
  }
};
const billId = () => page.url().match(/bill\/(bill_[0-9A-Z]{26})/)?.[1];

// 1. Billing: new bill, tap two items, take cash -----------------------------------------------------
let cashBill;
await step('bill: new bill, tap 2 items, take cash', async () => {
  await go('/device/bill');
  await page.waitForURL(/\/device\/bill\/bill_/, { timeout: 20000 });
  cashBill = billId();
  const tiles = page.locator('.grid-cols-3 > button');
  await tiles.first().waitFor({ timeout: 15000 });
  await tiles.nth(0).click();
  await page.waitForTimeout(800);
  await tiles.nth(1).click();
  await until(async () => (await api(`/v1/views/bill/${cashBill}`)).bill.lines.length === 2);
  await page.getByRole('button', { name: 'Cash', exact: true }).last().click();
  await page.getByRole('button', { name: /Take cash/ }).click();
  await page.waitForURL(/\/paid/, { timeout: 20000 });
  const bill = (await api(`/v1/views/bill/${cashBill}`)).bill;
  if (bill.status !== 'closed') throw new Error(`bill status ${bill.status}`);
});

// 2. Udhaar: new bill, attach a khata customer, put in khata, owner says haan on the gate ----------------
await step('khata: sell on credit from the bill, approve the R2 read-back', async () => {
  const accounts = (await api('/v1/views/khata')).accounts.filter(
    (a) => a.limit_paise - a.balance_paise > 50000,
  );
  const who = accounts[0];
  const before = who.balance_paise;
  await go('/device/bill');
  await page.waitForURL(/\/device\/bill\/bill_/, { timeout: 20000 });
  const id = billId();
  await page.locator('.grid-cols-3 > button').first().click();
  await until(async () => (await api(`/v1/views/bill/${id}`)).bill.lines.length === 1);
  await page.getByRole('button', { name: 'Khata', exact: true }).last().click(); // the payment chip, not the rail tab
  await page.getByRole('button', { name: /Put in khata/ }).click(); // no customer yet: the picker opens
  await page.getByPlaceholder(/Name, phone or UPI/).fill(who.display_name.split(' ')[0]);
  await page.getByText(who.display_name).first().click();
  await until(async () => (await api(`/v1/views/bill/${id}`)).bill.patron_id === who.patron_id);
  await page.getByRole('button', { name: /Put in khata/ }).click();
  await page.waitForTimeout(1500);
  await go('/device/gate');
  await page.waitForURL(/\/device\/gate\/gate_/, { timeout: 15000 });
  await page.getByRole('button', { name: /Yes, go ahead/ }).click();
  await until(async () => (await api(`/v1/views/khata/${who.patron_id}`)).balance_paise > before, 60000);
});

// 3. Stock and a new item from the Learn form ----------------------------------------------------------
await step('stock: screen loads; Learn adds a new item (R2)', async () => {
  await go('/device/stock');
  await page
    .getByText(/Goods in|Stock/)
    .first()
    .waitFor();
  await go('/device/learn');
  const name = `UI Flow Namkeen ${Date.now() % 10000}`;
  const inputs = page.locator('main input, input');
  await inputs.nth(0).fill(name); // name
  await page.locator('input[type=number]').nth(0).fill('40'); // MRP
  await page.locator('input[type=number]').nth(1).fill('38'); // price
  await page.locator('input[type=number]').nth(2).fill('30'); // cost
  await page.getByRole('button', { name: /Yes, add it/ }).click();
  await page.waitForTimeout(1500);
  const gate = await api('/v1/views/latest/gate');
  if (gate.id && (await api(`/v1/views/gates/${gate.id}`)).gate.status === 'pending') {
    await go(`/device/gate/${gate.id}`);
    const yes = page.getByRole('button', { name: /Yes, go ahead/ });
    if (await yes.count()) await yes.click();
  }
  await until(async () => (await api('/v1/views/stock')).items.some((i) => i.name === name), 60000);
});

// 4. Khata screen, customer page --------------------------------------------------------------------
await step('khata: list and a customer account open', async () => {
  await go('/device/khata');
  await page.getByText(/Khata/).first().waitFor();
  await go('/device/patron');
  await page.waitForURL(/\/device\/patron\/pat_/, { timeout: 15000 });
});

// 5. Ask Arth through the dock (live LLM) -----------------------------------------------------------
await step('ask: dock question answered by the AI', async () => {
  await go('/device/home');
  const dock = page.getByPlaceholder(/Speak or type/);
  await dock.fill('kitna udhaar baaki hai');
  await dock.press('Enter');
  await until(async () => log.some((l) => l.path === '/v1/turns' && l.status === 200), 30000);
});

await browser.close();
writeFileSync(join(OUT, 'requests.json'), JSON.stringify(log, null, 2));
const writes = log.filter((l) => l.method !== 'GET');
const failed = log.filter((l) => l.status >= 400);
console.log(results.join('\n'));
console.log(
  `\n${log.length} backend requests (${writes.length} writes), ${failed.length} failed · log: ${join(OUT, 'requests.json')}`,
);
process.exit(results.some((r) => r.startsWith('FAIL')) ? 1 : 0);
