// tokens.json -> app/tokens.css (Tailwind v4 @theme + device CSS variables).
// Run via: python dev.py gen   (or: pnpm --filter frontend run tokens)
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const FRONTEND = join(dirname(fileURLToPath(import.meta.url)), '..');
await mkdir(join(FRONTEND, 'app'), { recursive: true });
const tokens = JSON.parse(await readFile(join(FRONTEND, '..', 'contracts', 'tokens.json'), 'utf-8'));

const lines = [
  '/* Generated from contracts/tokens.json. Do not edit; run `python dev.py gen`. */',
  '@theme {',
];
for (const [name, value] of Object.entries(tokens.color)) lines.push(`  --color-${name}: ${value};`);
for (const [name, value] of Object.entries(tokens.shadow)) lines.push(`  --shadow-${name}: ${value};`);
for (const [name, value] of Object.entries(tokens.radius)) lines.push(`  --radius-${name}: ${value};`);
lines.push(`  --font-sans: ${tokens.font.sans};`);
for (const [name, [size, weight]] of Object.entries(tokens.text)) {
  lines.push(`  --text-${name}: ${size};`);
  lines.push(`  --text-${name}--font-weight: ${weight};`);
}
lines.push('}', '', ':root {');
for (const [name, value] of Object.entries(tokens.device)) lines.push(`  --device-${name}: ${value}px;`);
lines.push('}', '');

await writeFile(join(FRONTEND, 'app', 'tokens.css'), lines.join('\n'));
console.log('tokens: wrote app/tokens.css');
