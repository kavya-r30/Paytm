// Stage evidence check: a fresh browser opens the stage, asks Arth a question in the device iframe, then reads
// the Trace, AI calls, Tools and Logs tabs. Usage: node scripts/stage-evidence.mjs ["question"]
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'e2e-output', 'stage-evidence');
mkdirSync(OUT, { recursive: true });
const question = process.argv[2] ?? 'Priya ka khata kitna hai aur aaj kitna aaya?';
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1700, height: 960 } })).newPage();
await page.goto('http://localhost:3000/stage?lang=en', { waitUntil: 'load' });
await page.waitForTimeout(9000); // live session + reload + iframes
const device = page.frameLocator('iframe[title="device"]');
const dock = device.getByPlaceholder(/Speak or type|Bolo ya likho/);
await dock.fill(question);
await dock.press('Enter');
await page.waitForTimeout(12000);
for (const tab of ['Trace', 'AI calls', 'Tools', 'Logs']) {
  await page.getByRole('button', { name: tab, exact: true }).click();
  await page.waitForTimeout(800);
  const panel = (await page.locator('body').innerText()).replace(/\s+/g, ' ');
  const at = panel.indexOf('Health');
  console.log(`\n[${tab}] ${panel.slice(at + 6, at + 420)}`);
  await page.screenshot({ path: join(OUT, `${tab.replace(/\W+/g, '_')}.png`) });
}
await browser.close();
console.log(`\nscreenshots: ${OUT}`);
