// Kirana Reorder playbook, live (T5.8, E7.1): Arth drafts a PO for an item, the owner says haan on the device
// gate, the supplier confirms and delivers short against a full bill, the 3-way match finds the variance and
// the playbook asks to send a claim, which the owner approves. Records every backend request.
// Usage (API :8000 with one seeded shop, web :3000): node scripts/playbook-flow.mjs [--headed]
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const WEB = 'http://localhost:3000';
const API = 'http://localhost:8000';
const OUT = join(ROOT, 'e2e-output', 'playbook');
mkdirSync(OUT, { recursive: true });

const director = { 'Content-Type': 'application/json', Authorization: 'Bearer dev-director' };
const token = (
  await (
    await fetch(`${API}/v1/director/session`, {
      method: 'POST',
      headers: director,
      body: '{"surface":"device"}',
    })
  ).json()
).token;
const auth = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
const get = async (path) => (await fetch(`${API}${path}`, { headers: auth })).json();
const command = async (type, payload) => {
  const res = await fetch(`${API}/v1/commands`, {
    method: 'POST',
    headers: { ...auth, 'Idempotency-Key': crypto.randomUUID() },
    body: JSON.stringify({ type, payload }),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(`${type} ${res.status} ${JSON.stringify(body).slice(0, 200)}`);
  return body;
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const until = async (what, fn, ms = 90000) => {
  const end = Date.now() + ms;
  for (;;) {
    const v = await fn();
    if (v) return v;
    if (Date.now() > end) throw new Error(`timed out: ${what}`);
    await sleep(1500);
  }
};
const lines = [];
const say = (s) => {
  lines.push(s);
  console.log(s);
};

const log = [];
const browser = await chromium.launch({ headless: !process.argv.includes('--headed') });
const context = await browser.newContext({ viewport: { width: 1280, height: 960 } });
await context.addInitScript((t) => localStorage.setItem('arth.session', t), token);
const page = await context.newPage();
page.on('response', (r) => {
  if (!r.url().startsWith(API) || r.url().includes('/v1/stream') || r.request().method() === 'GET') return;
  let type = '';
  try {
    type = JSON.parse(r.request().postData() ?? '{}').type ?? '';
  } catch {
    // not JSON
  }
  log.push({
    who: 'device UI',
    method: r.request().method(),
    path: r.url().slice(API.length),
    type,
    status: r.status(),
  });
});
const approveOnDevice = async (gateId, label) => {
  await page.goto(`${WEB}/device/gate/${gateId}?lang=en`, { waitUntil: 'load' });
  await page.getByRole('button', { name: /Yes, go ahead/ }).click({ timeout: 20000 });
  await sleep(1200);
  const again = page.getByRole('button', { name: /Yes, go ahead|Confirm/ }); // R3 asks twice
  if (await again.count())
    await again
      .first()
      .click()
      .catch(() => {});
  await page.screenshot({ path: join(OUT, `${label}.png`) });
};

try {
  // 1. start: an item running low gets a Reorder run (Night Shift starts these; here the owner asks for one)
  const stock = (await get('/v1/views/stock')).items;
  const item = stock.find((i) => i.status !== 'ok') ?? stock[0];
  await command('playbooks.start', { playbook: 'reorder', subject: item.item_id });
  say(`1  playbooks.start reorder for ${item.name}`);
  const run = await until('reorder run', async () =>
    (await get('/v1/views/team')).runs?.find((r) => r.playbook === 'reorder' && r.subject === item.item_id),
  );
  say(`   run ${run.id ?? run.run_id} started`);

  // 2. Arth drafted the PO and asks the owner to place it (R3 gate) -> owner says haan on the device
  const placeGate = await until('PO gate', async () =>
    (await get('/v1/views/notifications')).needs_you.find((g) => g.type === 'supply.place_po'),
  );
  const poId = placeGate.scope?.payload?.po_id ?? (await get('/v1/views/latest/po')).id;
  say(`2  gate ${placeGate.gate_id}: place ${poId}; owner approves on the device`);
  await approveOnDevice(placeGate.gate_id, 'place_po_gate');
  await until('PO sent', async () => (await get(`/v1/views/po/${poId}`)).po?.status === 'sent');
  say('   PO sent to the supplier');

  // 3. supplier confirms, delivers 45 of 50, bills for 50 -> 3-way match variance
  const po = (await get(`/v1/views/po/${poId}`)).po;
  const line = po.lines[0];
  await command('supply.confirm_po', { po_id: poId });
  await command('supply.receive', {
    po_id: poId,
    lines: [{ item_id: line.item_id, qty_milli: line.qty_milli - 5000 }],
  });
  const due = new Date(Date.now() + 7 * 864e5).toISOString().slice(0, 10);
  const bill = await command('supply.record_bill', {
    po_id: poId,
    bill_ref: `INV-${Date.now() % 100000}`,
    lines: [{ item_id: line.item_id, qty_milli: line.qty_milli, unit_price_paise: line.unit_price_paise }],
    due_on: due,
  });
  say('3  supplier confirmed; received 5 short; bill for the full quantity entered');
  if (bill.status === 'needs_approval') {
    say(`   gate ${bill.gate_id}: supplier bill read-back (R2); owner approves on the device`);
    await approveOnDevice(bill.gate_id, 'record_bill_gate');
  }

  // 4. the playbook wakes on po.variance_found and asks to send the claim (R3) -> owner approves
  const claimGate = await until('claim gate', async () =>
    (await get('/v1/views/notifications')).needs_you.find((g) => g.type === 'supply.send_claim'),
  );
  say(`4  gate ${claimGate.gate_id}: send claim; owner approves on the device`);
  await approveOnDevice(claimGate.gate_id, 'send_claim_gate');

  // 5. the run is done and the claim is sent; the Run screen shows the timeline
  const runId = run.id ?? run.run_id;
  const done = await until('run done', async () => {
    const view = await get(`/v1/views/runs/${runId}`);
    return view.run?.status === 'done' ? view : null;
  });
  const claim = (await get('/v1/views/latest/claim')).id;
  say(
    `5  run ${runId} done (${done.steps?.length ?? '?'} steps); claim ${claim} ${(await get(`/v1/views/claims/${claim}`)).claim?.status}`,
  );
  await page.goto(`${WEB}/device/run/${runId}?lang=en`, { waitUntil: 'load' });
  await sleep(2000);
  await page.screenshot({ path: join(OUT, 'run_screen.png') });
  say('PLAYBOOK GREEN');
} catch (e) {
  say(`PLAYBOOK FAILED: ${e.message}`);
  process.exitCode = 1;
} finally {
  await browser.close();
  writeFileSync(join(OUT, 'device-requests.json'), JSON.stringify(log, null, 2));
  console.log(
    `\ndevice UI writes:\n${log.map((l) => `  ${l.method} ${l.path} ${l.type} -> ${l.status}`).join('\n')}`,
  );
}
