import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { SCHEMAS, type SchemaName } from '../lib/contracts';
import { parseEnvelope, validate, validateEnvelope, validateEvent, validateProblem } from '../lib/validate';

const EXAMPLES_DIR = fileURLToPath(new URL('../../contracts/examples/', import.meta.url));
const examples = readdirSync(EXAMPLES_DIR)
  .filter((f) => f.endsWith('.example.json'))
  .sort()
  .map(
    (f) => [f.replace(/\.example\.json$/, ''), JSON.parse(readFileSync(EXAMPLES_DIR + f, 'utf-8'))] as const,
  );
const example = (name: string) => structuredClone(examples.find(([n]) => n === name)![1]);
const contractNames = [
  'approval',
  'approval_decided',
  'approval_requested',
  'audit_verification',
  'audit_verified',
  'batch_recalled',
  'catalog_add_item',
  'catalog_bulk_price',
  'catalog_change_price',
  'catalog_import_items',
  'catalog_item_added',
  'catalog_item_view',
  'catalog_price_changed',
  'catalog_search_view',
  'command',
  'command_executed',
  'command_result',
  'common',
  'consent_grant',
  'consent_stop',
  'consent_withdraw',
  'credit_changed',
  'credit_payable_changed',
  'credit_receipt_requested',
  'credit_reminder_requested',
  'credit_statement_requested',
  'customer_search_view',
  'envelope',
  'event',
  'expiry_view',
  'i18n_changed',
  'khata_account_view',
  'khata_view',
  'ledger_acknowledge_entry',
  'ledger_add_entry',
  'ledger_add_payable',
  'ledger_apply_advance',
  'ledger_apply_verified_payment',
  'ledger_dispute_entry',
  'ledger_open_account',
  'ledger_pay_payable',
  'ledger_record_deposit',
  'ledger_record_payment',
  'ledger_record_promise',
  'ledger_resolve_dispute',
  'ledger_reverse_entry',
  'ledger_send_reminder',
  'ledger_send_statement',
  'ledger_set_limit',
  'ledger_statement_view',
  'merchant_bootstrap',
  'merchant_update_settings',
  'onboarding_complete_step',
  'onboarding_started',
  'onboarding_updated',
  'onboarding_view',
  'patron_changed',
  'patron_consent_changed',
  'patron_merged',
  'patron_reward_changed',
  'patron_view',
  'patrons_add',
  'patrons_add_command',
  'patrons_add_household_member',
  'patrons_merge',
  'patrons_propose_merge',
  'patrons_update_command',
  'patrons_update_profile',
  'payables_view',
  'problem',
  'promises_view',
  'resolution_view',
  'rewards_configure',
  'rewards_record_visit',
  'rewards_redeem',
  'session_result',
  'settings_view',
  'shift_close',
  'shift_open',
  'shift_view',
  'staff_add',
  'staff_add_command',
  'staff_added',
  'staff_logged_in',
  'staff_login',
  'staff_login_command',
  'staff_logout',
  'staff_shift_closed',
  'staff_shift_opened',
  'staff_view',
  'stock_adjust',
  'stock_changed',
  'stock_count',
  'stock_demand_logged',
  'stock_log_unmet_demand',
  'stock_override_recorded',
  'stock_recall_batch',
  'stock_receive',
  'stock_view',
  'view_invalidate',
];

describe('contract registry', () => {
  it('lists every contract', () => {
    expect(SCHEMAS.map((s) => s.name).sort()).toEqual(contractNames);
  });

  it('has an example for each top-level contract', () => {
    expect(examples.map(([n]) => n)).toEqual(contractNames.filter((name) => name !== 'common'));
  });
});

describe.each(examples)('%s example', (name, data) => {
  it('validates against its schema', () => {
    expect(validate(name as SchemaName, data)).toBe(true);
  });
});

describe('envelope contract', () => {
  it('accepts the spec example via the named validator', () => {
    expect(validateEnvelope(example('envelope'))).toBe(true);
  });

  it('rejects an unknown audience', () => {
    expect(validateEnvelope({ ...example('envelope'), audience: 'everyone' })).toBe(false);
  });

  it('rejects an unknown card type', () => {
    expect(validateEnvelope({ ...example('envelope'), cards: [{ type: 'banner' }] })).toBe(false);
  });

  it('rejects hi-Latn as a speech locale (resolved through common.schema.json)', () => {
    expect(validateEnvelope({ ...example('envelope'), lang: { screen: 'hi-Latn', speech: 'hi-Latn' } })).toBe(
      false,
    );
  });

  it('rejects a bad undo date-time (formats are on)', () => {
    const bad = example('envelope');
    bad.undo.until = 'yesterday';
    expect(validateEnvelope(bad)).toBe(false);
  });

  it('parseEnvelope returns the typed envelope or throws with the errors', () => {
    expect(parseEnvelope(example('envelope')).turn_id).toMatch(/^turn_/);
    expect(() => parseEnvelope({ ...example('envelope'), presence: { state: 'dancing' } })).toThrow(
      /invalid envelope: .*presence\/state/,
    );
  });
});

describe('event and problem contracts', () => {
  it('rejects an event type without a dot', () => {
    expect(validateEvent({ ...example('event'), type: 'ticked' })).toBe(false);
  });

  it('accepts a root event with a null causation_id', () => {
    expect(validateEvent({ ...example('event'), causation_id: null })).toBe(true);
  });

  it('rejects a problem with a 2xx status', () => {
    expect(validateProblem({ ...example('problem'), status: 200 })).toBe(false);
  });

  it('throws for an unknown contract name', () => {
    expect(() => validate('nope' as SchemaName, {})).toThrow(/no contract named "nope"/);
  });
});
