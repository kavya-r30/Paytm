// Generates TS types from the contracts, copies the schemas for Ajv, and writes the registry.
// Run via: python dev.py gen        (or: pnpm --filter frontend run gen)
//          python dev.py gen-check  (or: pnpm --filter frontend run gen:check) exits 1 when stale
//
// Every contracts/**/*.schema.json outside examples/ and fixtures/ is a contract named by its file
// stem (events/event.schema.json -> "event"); its `title` names the TS type. Outputs, all under
// lib/contracts/: <name>.ts, schemas/<name>.schema.json, api.ts (openapi.yaml) and index.ts.
// Nothing is written unless every contract compiles.
import { compileFromFile } from 'json-schema-to-typescript';
import openapiTS, { astToString } from 'openapi-typescript';
import { mkdir, readdir, readFile, unlink, writeFile } from 'node:fs/promises';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const FRONTEND = join(dirname(fileURLToPath(import.meta.url)), '..');
const CONTRACTS = join(FRONTEND, '..', 'contracts');
const OUT = join(FRONTEND, 'lib', 'contracts');
const BANNER = '/* Generated from contracts. Do not edit; run `python dev.py gen`. */';
const SUFFIX = '.schema.json';
const EXCLUDED = new Set(['examples', 'fixtures']);
const STALE = 'contracts are stale: run `python dev.py gen`';

class GenError extends Error {}

async function discover(dir = CONTRACTS) {
  const found = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!(dir === CONTRACTS && EXCLUDED.has(entry.name))) found.push(...(await discover(path)));
    } else if (entry.name.endsWith(SUFFIX)) {
      found.push({ name: entry.name.slice(0, -SUFFIX.length), path });
    }
  }
  return found;
}

async function contracts() {
  const byName = new Map();
  for (const c of (await discover()).sort((a, b) => a.name.localeCompare(b.name))) {
    const rel = relative(CONTRACTS, c.path).split(sep).join('/');
    if (byName.has(c.name)) {
      throw new GenError(`duplicate contract name "${c.name}": ${byName.get(c.name).rel} and ${rel}`);
    }
    const text = await readFile(c.path, 'utf-8');
    const schema = JSON.parse(text);
    if (typeof schema.title !== 'string' || !schema.title) {
      throw new GenError(`${rel}: a contract schema needs a non-empty "title" (the generated type name)`);
    }
    byName.set(c.name, { ...c, rel, text, schema, title: schema.title });
  }
  return [...byName.values()];
}

const toLf = (s) => s.replace(/\r\n/g, '\n');

function indexTs(all) {
  const lines = [BANNER, ''];
  for (const c of all) lines.push(`import type { ${c.title} } from './${c.name}';`);
  for (const c of all) lines.push(`import ${c.name}Schema from './schemas/${c.name}${SUFFIX}';`);
  lines.push('');
  for (const c of all) lines.push(`export type { ${c.title} } from './${c.name}';`);
  lines.push(
    "export type * from './common'; // shared definitions: Locale, SpeechLocale, Audience, Tier, ...",
  );
  lines.push(
    '',
    '/** Every contract: name (file stem), JSON Schema $id and the schema itself, for Ajv. */',
    'export const SCHEMAS = [',
    ...all.map((c) => `  { name: '${c.name}', id: '${c.schema.$id}', schema: ${c.name}Schema },`),
    '] as const;',
    '',
    "export type SchemaName = (typeof SCHEMAS)[number]['name'];",
    '',
    '/** The generated type for each contract name. */',
    'export interface ContractTypes {',
    ...all.map((c) => `  ${c.name}: ${c.title};`),
    '}',
    '',
  );
  return lines.join('\n');
}

async function render() {
  const all = await contracts();
  const files = new Map();
  const failures = [];
  for (const c of all) {
    try {
      // unreachableDefinitions: a definitions-only schema (common) still exports each definition as a type.
      const ts = await compileFromFile(c.path, {
        bannerComment: BANNER,
        cwd: dirname(c.path),
        unreachableDefinitions: true,
      });
      if (!new RegExp(`^export (interface|type) ${c.title}\\b`, 'm').test(ts)) {
        throw new GenError(`no exported type named "${c.title}" (the schema title)`);
      }
      files.set(`${c.name}.ts`, toLf(ts));
      files.set(`schemas/${c.name}${SUFFIX}`, toLf(c.text));
    } catch (err) {
      failures.push(`${c.rel}: ${err instanceof Error ? err.message : String(err)}`);
    }
  }
  try {
    const ast = await openapiTS(pathToFileURL(join(CONTRACTS, 'openapi.yaml')));
    files.set('api.ts', `${BANNER}\n\n${toLf(astToString(ast))}`);
  } catch (err) {
    failures.push(`openapi.yaml: ${err instanceof Error ? err.message : String(err)}`);
  }
  if (failures.length) throw new GenError(`code generation failed:\n  ${failures.join('\n  ')}`);
  files.set('index.ts', indexTs(all));
  return new Map([...files].sort(([a], [b]) => a.localeCompare(b)));
}

/** Generated files on disk: top-level *.ts and schemas/*.json under lib/contracts. */
async function existing() {
  const list = async (sub, ext) => {
    try {
      const entries = await readdir(join(OUT, sub), { withFileTypes: true });
      return entries
        .filter((e) => e.isFile() && e.name.endsWith(ext))
        .map((e) => (sub ? `${sub}/${e.name}` : e.name));
    } catch {
      return [];
    }
  };
  return [...(await list('', '.ts')), ...(await list('schemas', '.json'))];
}

async function stale(files) {
  const out = [];
  for (const [rel, content] of files) {
    const current = await readFile(join(OUT, rel), 'utf-8').catch(() => null);
    if (current !== content) out.push(rel);
  }
  for (const rel of await existing()) if (!files.has(rel)) out.push(rel);
  return out.sort();
}

async function main() {
  const check = process.argv.includes('--check');
  const files = await render();
  if (check) {
    const changed = await stale(files);
    if (changed.length) {
      console.error(`${STALE}\n${changed.map((f) => `  frontend/lib/contracts/${f}`).join('\n')}`);
      process.exitCode = 1;
      return;
    }
    console.log(`contracts: ${files.size} frontend files are up to date`);
    return;
  }
  await mkdir(join(OUT, 'schemas'), { recursive: true });
  for (const [rel, content] of files) await writeFile(join(OUT, rel), content);
  for (const rel of await existing()) {
    if (!files.has(rel)) {
      await unlink(join(OUT, rel));
      console.log(`contracts: removed stale lib/contracts/${rel}`);
    }
  }
  console.log(`contracts: wrote ${files.size} files to lib/contracts`);
}

try {
  await main();
} catch (err) {
  console.error(`gen-contracts: ${err instanceof Error ? err.message : String(err)}`);
  process.exitCode = 1;
}
