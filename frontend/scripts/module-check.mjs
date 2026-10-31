// Module-by-module check in a FRESH browser (no injected session, like a person opening the app): each module
// runs its screen actions and its AI questions through the ask dock, logging every backend call and what the
// screen shows. Usage: node scripts/module-check.mjs <module> [--web http://127.0.0.1:3000] [--headed]
// Modules: ai, billing, khata, stock, supply, orders, growth, money, agents, settings
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const arg = (n, d) =>
  process.argv.includes(`--${n}`) ? process.argv[process.argv.indexOf(`--${n}`) + 1] : d;
const MODULE = process.argv[2];
const WEB = arg('web', 'http://127.0.0.1:3000');
const API = 'http://localhost:8000';
const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'e2e-output', 'modules', MODULE);
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ headless: !process.argv.includes('--headed') });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 960 } })).newPage();
const calls = [];
const problems = [];
page.on('pageerror', (e) => problems.push(`pageerror ${e.message.split('\n')[0]}`));
page.on('console', (m) => {
  if (m.type() === 'error' && !/favicon|DevTools/.test(m.text()))
    problems.push(`console ${m.text().slice(0, 200)}`);
});
page.on('response', async (r) => {
  if (!r.url().startsWith(API) || r.url().includes('/v1/stream') || r.request().method() === 'OPTIONS')
    return;
  let type = '';
  try {
    type = JSON.parse(r.request().postData() ?? '{}').type ?? '';
  } catch {
    // not JSON
  }
  const entry = `${r.request().method()} ${r.url().slice(API.length).split('?')[0]} ${type} -> ${r.status()}`;
  calls.push(entry);
  if (r.status() >= 400) problems.push(`${entry} ${(await r.text().catch(() => '')).slice(0, 160)}`);
});

const body = async () => (await page.locator('body').innerText()).replace(/\s+/g, ' ');
let n = 0;
async function step(label, fn) {
  const from = calls.length;
  const p0 = problems.length;
  let note = '';
  try {
    note = (await fn()) ?? '';
  } catch (e) {
    problems.push(`${label}: ${String(e.message ?? e).split('\n')[0]}`);
  }
  n += 1;
  await page.screenshot({
    path: join(OUT, `${String(n).padStart(2, '0')}_${label.replace(/\W+/g, '_').slice(0, 40)}.png`),
  });
  const mine = problems.slice(p0);
  console.log(`${mine.length ? 'FAIL' : 'ok  '}  ${label}${note ? `\n      shows: ${note}` : ''}`);
  for (const c of calls.slice(from).filter((c) => !c.startsWith('GET'))) console.log(`      ${c}`);
  for (const m of mine) console.log(`      !! ${m}`);
}
const open = async (path) => {
  await page.goto(`${WEB}${path}${path.includes('?') ? '&' : '?'}lang=en`, { waitUntil: 'load' });
  await page.waitForTimeout(2500);
};
async function ask(question) {
  const before = calls.filter((c) => c.startsWith('POST /v1/turns')).length;
  if (!(await page.getByPlaceholder(/Bolo ya likho|Speak or type/).count())) await open('/device/home');
  const dock = page.getByPlaceholder(/Bolo ya likho|Speak or type/);
  await dock.fill(question);
  await dock.press('Enter');
  const end = Date.now() + 60000;
  while (calls.filter((c) => c.startsWith('POST /v1/turns')).length === before) {
    if (Date.now() > end) throw new Error('the dock never asked the backend');
    await page.waitForTimeout(300);
  }
  await page.waitForTimeout(2500);
  const said = await page
    .locator('main .text-arth.leading-snug, p.text-arth')
    .last()
    .innerText()
    .catch(() => '');
  return `${page.url().replace(WEB, '')} | Arth: ${said.slice(0, 160)}`;
}

// first load: the page must connect itself to the backend (no injected token)
await step('first load connects to the backend', async () => {
  await open('/device/home');
  let live = false;
  for (let i = 0; i < 40 && !live; i++) {
    live = await page.evaluate(() => !!localStorage.getItem('arth.session')).catch(() => false);
    if (!live) await page.waitForTimeout(750);
  }
  await page.waitForTimeout(1500);
  if (!live) throw new Error('no live session: the page is showing demo data');
  const text = await body();
  if (/Not connected|demo data/i.test(text)) throw new Error('banner/demo chip still shown');
  return text.slice(0, 140);
});

// backend truth, read with the page's own session (what the screen should be showing)
const api = async (path) => {
  const token = await page.evaluate(() => localStorage.getItem('arth.session'));
  return (await fetch(`${API}${path}`, { headers: { Authorization: `Bearer ${token}` } })).json();
};
const until = async (what, fn, ms = 20000) => {
  const end = Date.now() + ms;
  for (;;) {
    const v = await fn();
    if (v) return v;
    if (Date.now() > end) throw new Error(`timed out: ${what}`);
    await page.waitForTimeout(600);
  }
};
const billIdOf = () => page.url().match(/(bill_[0-9A-Z]{26})/)?.[1];
const lines = async (bill) => (await api(`/v1/views/bill/${bill}`)).bill.lines;
const panel = async () =>
  (
    await page
      .locator('ul')
      .last()
      .innerText()
      .catch(() => '')
  ).replace(/\s+/g, ' ');
const say = async (text) => {
  const dock = page.getByPlaceholder(/Bolo ya likho|Speak or type/);
  await dock.fill(text);
  await dock.press('Enter');
  await page.waitForTimeout(3500);
};

// the owner's haan on the newest pending gate, on the device's gate screen
const approveLatestGate = async () => {
  const gate = await until('a pending gate', async () => {
    const latest = await api('/v1/views/latest/gate');
    if (!latest.id) return null;
    return (await api(`/v1/views/gates/${latest.id}`)).gate.status === 'pending' ? latest.id : null;
  });
  await open(`/device/gate/${gate}`);
  await page.getByRole('button', { name: /Yes, go ahead/ }).click();
  await page.waitForTimeout(1500);
  return gate;
};

// first segments of every i18n key: a visible "bill.via_tap"-shaped token with one of them is an untranslated key
const KEY_PREFIXES = Object.keys(
  JSON.parse(
    await (await import('node:fs/promises')).readFile(join(OUT, '..', '..', '..', 'i18n', 'en.json'), 'utf8'),
  ),
).reduce((set, k) => set.add(k.split('.')[0]), new Set());
const rawKeys = (text) =>
  [...new Set(text.match(/\b[a-z_]+\.[a-z0-9_.]+\b/g) ?? [])].filter((k) =>
    KEY_PREFIXES.has(k.split('.')[0]),
  );
const NAV_LABELS = /^(Today|Bill|Khata|Stock|Grow|More|En · Hi|Hi · En|R|Aaj|Badhao)$/;

/** Screen sweep: real data, no raw keys, then each action button once (fresh load per click), plus questions. */
async function sweep(screens, questions = []) {
  for (const screen of screens) {
    let labels = [];
    await step(`screen /${screen}`, async () => {
      await open(`/device/${screen}`);
      const text = await body();
      const raw = rawKeys(text);
      if (raw.length) throw new Error(`untranslated keys on screen: ${raw.join(', ')}`);
      if (/Something went wrong|Not connected/.test(text)) throw new Error('error state shown');
      labels = await page
        .locator('button:visible:not([disabled])')
        .evaluateAll((els) =>
          els
            .filter((e) => !e.closest('nextjs-portal'))
            .map((e) => (e.getAttribute('aria-label') || e.innerText || '').trim()),
        );
      return `${page.url().replace(WEB, '')} | ${text.slice(0, 150)}`;
    });
    const actions = [...new Set(labels)].filter(
      (l) => l && !NAV_LABELS.test(l) && l.length < 60 && !/^(Speak|Bolo)|Next\.js/.test(l),
    );
    for (const label of actions.slice(0, 8)) {
      await step(`  /${screen} -> "${label}"`, async () => {
        await open(`/device/${screen}`);
        const before = calls.length;
        await page
          .getByRole('button', { name: label, exact: true })
          .or(page.getByRole('switch', { name: label, exact: true }))
          .first()
          .click({ timeout: 5000 });
        await page.waitForTimeout(2000);
        const raw = rawKeys(await body());
        if (raw.length) throw new Error(`untranslated keys after click: ${raw.join(', ')}`);
        const posted = calls.slice(before).filter((c) => !c.startsWith('GET'));
        return `${page.url().replace(WEB, '')}${posted.length ? '' : ' (no backend write)'}`;
      });
    }
  }
  for (const q of questions) await step(`ask "${q}"`, () => ask(q));
}

const MODULES = {
  // the AI agent driving every module from the dock: each step shows the screen it opened and Arth's caption
  async agent() {
    const caption = async () =>
      (await page.locator('.bg-sky p.text-arth').first().innerText().catch(() => '')).slice(0, 160);
    for (const q of [
      'Priya ka bill banao, 2 Parle-G aur ek Maggi',
      'khate mein daal do',
      'Diwali ke liye kya kar sakte hain?',
      'Maggi kitni bachi hai?',
      'kitna udhaar baaki hai?',
      'hi',
    ]) {
      await step(`dock "${q}"`, async () => {
        await ask(q);
        return `${page.url().replace(WEB, '').split('?')[0]} | caption: ${await caption()}`;
      });
    }
  },
  stock: () =>
    sweep(
      ['stock', 'item', 'expiry', 'suppliers', 'learn'],
      ['kaunsa maal khatam ho raha hai', 'Maggi kitni bachi hai', 'Surf Excel ka rate kya hai'],
    ),
  supply: () => sweep(['suppliers', 'po', 'grn', 'claim', 'gate'], ['kya pending hai']),
  orders: () => sweep(['orders', 'order', 'storefront', 'park'], ['orders dikhao']),
  growth: () =>
    sweep(
      ['grow', 'plan', 'demand', 'bundle', 'offers', 'offer', 'campaign', 'ledger'],
      ['is hafte sabse zyada kya bika', 'kal ki bikri kitni hogi'],
    ),
  money: () =>
    sweep(['hisaab', 'reports', 'verdict', 'capital', 'paid'], ['aaj kitna aaya', 'aaj kitne bill bane']),
  agents: () =>
    sweep(['home', 'notifications', 'team', 'run', 'memory', 'forecast', 'ask'], ['kya pending hai']),
  settings: () => sweep(['menu', 'language', 'staff', 'trust', 'health', 'onboarding', 'shift', 'pin'], []),
  async khata() {
    const accounts = (await api('/v1/views/khata')).accounts;
    const who = accounts.find((a) => a.balance_paise > 5000) ?? accounts[0];
    const first = who.display_name.split(' ')[0];
    const balance = async () => (await api(`/v1/views/khata/${who.patron_id}`)).balance_paise;
    await step('khata list shows every customer with real balances', async () => {
      await open('/device/khata');
      await page.getByText(who.display_name).first().waitFor({ timeout: 15000 });
      return (await body()).slice(0, 200);
    });
    await step(`open ${who.display_name}'s account`, async () => {
      await page.getByText(who.display_name).first().click();
      await page.waitForURL(/\/device\/khata\/pat_/, { timeout: 15000 });
      return (await body()).slice(0, 200);
    });
    await step('money received ₹10 (R2) -> owner approves -> balance down', async () => {
      const before = await balance();
      await page.getByLabel(/Amount received/).fill('10');
      await page.getByRole('button', { name: /Money received/ }).click();
      await approveLatestGate();
      await until('balance down by 10', async () => (await balance()) === before - 1000, 45000);
      return `₹${before / 100} -> ₹${(await balance()) / 100}`;
    });
    await step(`voice: "${first} ne 20 jama kiye" -> approve -> balance down`, async () => {
      const before = await balance();
      await open('/device/home');
      await say(`${first} ne 20 jama kiye`);
      await approveLatestGate();
      await until('balance down by 20', async () => (await balance()) === before - 2000, 45000);
      return `₹${before / 100} -> ₹${(await balance()) / 100}`;
    });
    await step(`ask "${first} ka khata kitna hai"`, () => ask(`${first} ka khata kitna hai`));
    await step("reminder: refused without the customer's consent, shown politely", async () => {
      await open(`/device/khata/${who.patron_id}`);
      await page.getByRole('button', { name: /Send WhatsApp reminder/ }).click();
      await page.waitForTimeout(2500);
      return (await body()).match(/(consent|permission|haan)[^.]*\./i)?.[0] ?? (await body()).slice(-160);
    });
    await step('patron: change language (PII-safe route)', async () => {
      await open(`/device/patron/${who.patron_id}`);
      await page.locator('select').first().selectOption('en');
      await until('lang en', async () => (await api(`/v1/views/patron/${who.patron_id}`)).lang === 'en');
      return 'lang en';
    });
    await step('"new entry" starts a bill (udhaar is written with its items)', async () => {
      await open('/device/khata');
      await page.getByRole('button', { name: /New credit/ }).click();
      await page.waitForURL(/\/device\/bill/, { timeout: 15000 });
      return page.url().replace(WEB, '');
    });
  },
  async billing() {
    let bill;
    await step('new bill opens once', async () => {
      await open('/device/bill');
      await page.waitForURL(/\/device\/bill\/bill_/, { timeout: 20000 });
      bill = billIdOf();
      return bill;
    });
    await step('tap two items', async () => {
      const tiles = page.locator('.grid-cols-3 > button');
      await tiles.nth(0).click();
      await page.waitForTimeout(700);
      await tiles.nth(1).click();
      await until('2 lines', async () => (await lines(bill)).length === 2);
      await page.waitForTimeout(1500);
      return panel();
    });
    await step('voice: "ek Tata Salt aur" adds to this bill', async () => {
      await say('ek Tata Salt aur');
      await until('3 lines', async () => (await lines(bill)).length === 3);
      return `${page.url().replace(WEB, '')} | ${await panel()}`;
    });
    await step('voice: "hatao" removes the last line', async () => {
      await say('hatao');
      await until('2 lines', async () => (await lines(bill)).length === 2);
      return panel();
    });
    await step('park the bill, resume it from the park list', async () => {
      await page.getByRole('button', { name: 'Hold bill', exact: true }).click();
      await page.waitForURL(/\/device\/park/, { timeout: 15000 });
      await page.getByRole('button', { name: 'Resume', exact: true }).last().click();
      await page.waitForURL(/\/device\/bill\/bill_/, { timeout: 15000 });
      return page.url().replace(WEB, '');
    });
    await step('take cash, paid screen', async () => {
      await page
        .getByRole('button', { name: /^Cash$/ })
        .last()
        .click();
      await page.getByRole('button', { name: /Cash lo|Take cash/ }).click();
      await page.waitForURL(/\/paid/, { timeout: 20000 });
      const status = (await api(`/v1/views/bill/${bill}`)).bill.status;
      if (status !== 'closed') throw new Error(`bill ${status}`);
      return (await body()).slice(0, 160);
    });
    await step('return one item for cash', async () => {
      await open(`/device/return/${bill}`);
      await page.locator('input[type=number]').first().fill('1');
      await page.getByRole('button', { name: /Confirm return|Wapsi pakki/ }).click();
      await page.waitForTimeout(2500);
      return (await body()).slice(0, 120);
    });
    await step('UPI: QR, customer pays on the pay page, bill paid', async () => {
      await open('/device/bill');
      await page.waitForURL(/\/device\/bill\/bill_/, { timeout: 20000 });
      const upiBill = billIdOf();
      await page.locator('.grid-cols-3 > button').first().click();
      await until('1 line', async () => (await lines(upiBill)).length === 1);
      await page.getByRole('button', { name: /^Show QR ·/ }).click();
      await page.waitForURL(/\/pay/, { timeout: 20000 });
      const href = await until('pay link', () =>
        page.locator('a[href^="/pay/"]').first().getAttribute('href'),
      );
      const customer = await page.context().newPage();
      await customer.goto(`${WEB}${href}`);
      await customer.getByRole('button', { name: /^Pay/ }).first().click();
      await until(
        'bill closed',
        async () => (await api(`/v1/views/bill/${upiBill}`)).bill.status === 'closed',
        30000,
      );
      await customer.close();
      await page.waitForTimeout(2500);
      return `${page.url().replace(WEB, '')} | ${(await body()).slice(0, 100)}`;
    });
  },
  async ai() {
    for (const q of [
      'aaj kitna aaya',
      'aaj kitne bill bane',
      'Tata Salt kitna bacha hai',
      'Toor Dal ka rate kya hai',
      'Priya ka khata kitna hai',
      'khata kitna baaki hai',
      'kaunsa maal khatam ho raha hai',
      'is hafte sabse zyada kya bika',
      'kal ki bikri kitni hogi',
      'kya pending hai',
    ])
      await step(`ask "${q}"`, () => ask(q));
  },
};

if (!MODULES[MODULE]) console.log(`unknown module ${MODULE}; choose ${Object.keys(MODULES).join(', ')}`);
else await MODULES[MODULE]();
await browser.close();
console.log(
  `\n${MODULE}: ${problems.length ? `${problems.length} problem(s)` : 'all good'} · screenshots ${OUT}`,
);
process.exit(problems.length ? 1 : 0);
