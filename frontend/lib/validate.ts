// Runtime validation against the contract JSON Schemas (hand-written; the registry is generated).
// Every schema is added up front so cross-file $refs (common.schema.json) resolve by $id; each
// validator is compiled on first use and memoised by Ajv.
import Ajv, { type ValidateFunction } from 'ajv';
import addFormats from 'ajv-formats';
import { SCHEMAS, type ContractTypes, type Envelope, type SchemaName } from './contracts';

// strict: true with no exemptions. The contracts avoid union `type` arrays (see contracts/README.md),
// so neither strictTypes nor allowUnionTypes needs relaxing.
const ajv = new Ajv({ allErrors: true, strict: true });
addFormats(ajv);
for (const { schema } of SCHEMAS) ajv.addSchema(schema);

const ID_BY_NAME: Record<string, string> = Object.fromEntries(SCHEMAS.map((s) => [s.name, s.id]));

export function validator<N extends SchemaName>(name: N): ValidateFunction<ContractTypes[N]> {
  const id = ID_BY_NAME[name];
  if (!id) throw new Error(`no contract named "${name}"; known: ${Object.keys(ID_BY_NAME).join(', ')}`);
  const fn = ajv.getSchema<ContractTypes[N]>(id);
  if (!fn) throw new Error(`contract "${name}" (${id}) is not registered with Ajv`);
  return fn;
}

/** Validate data against a contract by name; on failure, `validator(name).errors` holds the reasons. */
export function validate<N extends SchemaName>(name: N, data: unknown): data is ContractTypes[N] {
  return validator(name)(data);
}

type NamedValidator<T> = ((data: unknown) => data is T) & { readonly errors: ValidateFunction['errors'] };

/** A validator bound to one contract, compiled on first call; `.errors` mirrors Ajv's last result. */
function lazy<N extends SchemaName>(name: N): NamedValidator<ContractTypes[N]> {
  const fn = (data: unknown): data is ContractTypes[N] => validate(name, data);
  return Object.defineProperty(fn, 'errors', { get: () => validator(name).errors }) as NamedValidator<
    ContractTypes[N]
  >;
}

export const validateEnvelope = lazy('envelope');
export const validateEvent = lazy('event');
export const validateProblem = lazy('problem');

/** Return data typed as an Envelope, or throw with Ajv's error text. */
export function parseEnvelope(data: unknown): Envelope {
  const fn = validator('envelope');
  if (!fn(data)) throw new Error(`invalid envelope: ${ajv.errorsText(fn.errors)}`);
  return data;
}
