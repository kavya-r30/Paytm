// Design lint (spec I3, T7.1): no raw colours, radii, shadows or font sizes outside tokens.css, and no literal
// copy in product components (every label comes from the catalogue). Run by `pnpm run lint`.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const DIRS = ['app', 'components', 'screens'];
// The dev index and the generated token file are exempt.
const EXEMPT = new Set(['app/tokens.css', 'app/page.tsx', 'app/health-badge.tsx']);

const RULES = [
  { name: 'raw hex colour', re: /#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3}(?:[0-9a-fA-F]{2})?)?\b(?![\w-])/g },
  { name: 'raw rgb/hsl colour', re: /\b(?:rgba?|hsla?)\(/g },
  { name: 'arbitrary colour class', re: /\b[a-z]+-\[(?:#|rgb|hsl|color)/g },
  { name: 'arbitrary font size', re: /\btext-\[\d/g },
  { name: 'arbitrary radius', re: /\brounded(?:-[a-z]+)?-\[/g },
  { name: 'arbitrary shadow', re: /\bshadow-\[/g },
];
// JSX text that starts with a capitalised word of 3+ letters: a literal label that bypassed t().
const LITERAL = />\s*([A-Z][a-z]{2,}(?:\s+[a-z]+){1,})\s*</g;

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (/\.(tsx|ts|css)$/.test(name)) out.push(p);
  }
  return out;
}

const problems = [];
for (const d of DIRS) {
  for (const file of walk(join(ROOT, d))) {
    const rel = relative(ROOT, file).replace(/\\/g, '/');
    if (EXEMPT.has(rel)) continue;
    const lines = readFileSync(file, 'utf8').split('\n');
    lines.forEach((line, i) => {
      if (line.includes('lint-design-ok')) return;
      for (const rule of RULES) {
        for (const m of line.matchAll(rule.re)) problems.push(`${rel}:${i + 1} ${rule.name}: ${m[0]}`);
      }
      if (file.endsWith('.tsx')) {
        for (const m of line.matchAll(LITERAL)) problems.push(`${rel}:${i + 1} literal copy: "${m[1]}"`);
      }
    });
  }
}

if (problems.length) {
  console.error(problems.join('\n'));
  console.error(`\nlint-design: ${problems.length} problem(s). Use tokens and t('key').`);
  process.exit(1);
}
console.log('lint-design: ok');
