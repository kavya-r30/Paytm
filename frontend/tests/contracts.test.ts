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
  'action_snoozed',
  'actions_snooze',
  'agents_pause',
  'agents_paused',
  'alert_raised',
  'alerts_scan',
  'appointments_assign',
  'appointments_book',
  'appointments_transition',
  'appointments_view',
  'appointments_walk_in',
  'approval',
  'approval_decided',
  'approval_requested',
  'ask_view',
  'audit_verification',
  'audit_verified',
  'batch_recalled',
  'bill_changed',
  'bill_paid',
  'bill_paid_view',
  'bill_pay_view',
  'bill_price_override',
  'bill_returned',
  'bill_ticket_changed',
  'bill_view',
  'books_close_month',
  'books_month_closed',
  'bundles_view',
  'calendar_add_local_event',
  'calendar_local_event_added',
  'calendar_view',
  'campaign_view',
  'capital_applied',
  'capital_apply',
  'capital_offer_received',
  'capital_record_offer',
  'capital_view',
  'catalog_add_item',
  'catalog_bulk_price',
  'catalog_change_price',
  'catalog_import_items',
  'catalog_item_added',
  'catalog_item_view',
  'catalog_price_changed',
  'catalog_search_view',
  'chart_card',
  'claim_view',
  'command',
  'command_executed',
  'command_result',
  'common',
  'consent_grant',
  'consent_stop',
  'consent_withdraw',
  'counter_add_lines',
  'counter_advance_ticket',
  'counter_attach_patron',
  'counter_checkout',
  'counter_checkout_khata',
  'counter_open_bill',
  'counter_park',
  'counter_remove_line',
  'counter_request_upi',
  'counter_resume',
  'counter_return',
  'counter_send_to_kitchen',
  'counter_set_qty',
  'counter_undo',
  'counter_void_bill',
  'credit_changed',
  'credit_payable_changed',
  'credit_receipt_requested',
  'credit_reminder_requested',
  'credit_statement_requested',
  'customer_search_view',
  'demand_view',
  'device_health_reported',
  'device_report_health',
  'envelope',
  'event',
  'expiry_view',
  'feedback_record',
  'feedback_recorded',
  'feedback_view',
  'forecast_view',
  'gate_view',
  'grn_view',
  'grow_view',
  'growth_create_plan',
  'growth_ledger_view',
  'growth_outreach_requested',
  'growth_stop_campaign',
  'growth_updated',
  'health_view',
  'hint_offered',
  'hints_accept',
  'hisaab_view',
  'home_view',
  'i18n_changed',
  'insights_view',
  'khata_account_view',
  'khata_view',
  'kot_view',
  'latest_ref_view',
  'layer_pending_view',
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
  'memory_changed',
  'memory_confirm',
  'memory_forget',
  'memory_propose',
  'memory_retract',
  'memory_view',
  'merchant_bootstrap',
  'merchant_update_settings',
  'message_in',
  'message_out',
  'messages_receive',
  'messages_reply',
  'notifications_view',
  'offer_cashback_requested',
  'offer_clawed_back',
  'offer_detail_view',
  'offer_expired',
  'offer_issued',
  'offer_program_changed',
  'offer_redeemed',
  'offers_create_program',
  'offers_exclude_payers',
  'offers_expire_due',
  'offers_pause_program',
  'offers_view',
  'onboarding_complete_step',
  'onboarding_started',
  'onboarding_updated',
  'onboarding_view',
  'order_appointment_changed',
  'order_changed',
  'order_view',
  'orders_accept',
  'orders_advance',
  'orders_create_draft',
  'orders_decline',
  'orders_place',
  'orders_settle',
  'orders_substitute',
  'orders_view',
  'outreach_send_campaign',
  'park_view',
  'patron_changed',
  'patron_consent_changed',
  'patron_export',
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
  'payment_daily_closed',
  'payment_exception_opened',
  'payment_exception_resolved',
  'payment_expense_recorded',
  'payment_failed',
  'payment_matched',
  'payment_pending',
  'payment_received',
  'payment_refunded',
  'peers_view',
  'plan_view',
  'playbook_updated',
  'playbooks_cancel',
  'playbooks_start',
  'po_changed',
  'po_supplier_added',
  'po_variance_found',
  'po_view',
  'preorder_changed',
  'preorders_create',
  'privacy_erase_patron',
  'privacy_erased',
  'privacy_export_patron',
  'privacy_exported',
  'privacy_set_data_sharing',
  'privacy_sharing_changed',
  'problem',
  'promises_view',
  'public_storefront',
  'reports_view',
  'resolution_view',
  'rewards_configure',
  'rewards_record_visit',
  'rewards_redeem',
  'run_view',
  'rx_view',
  'scenario',
  'sentinel_check',
  'sentinel_verdict',
  'session_result',
  'settings_view',
  'settlement_recorded',
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
  'staff_set_skills',
  'staff_shift_closed',
  'staff_shift_opened',
  'staff_skills_set',
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
  'storefront_publish',
  'storefront_published',
  'storefront_view',
  'suppliers_view',
  'supply_add_supplier',
  'supply_cancel_po',
  'supply_confirm_po',
  'supply_draft_po',
  'supply_place_po',
  'supply_receive',
  'supply_record_bill',
  'supply_record_quote',
  'supply_send_claim',
  'tax_invoice_issued',
  'team_view',
  'treasury_daily_close',
  'treasury_expense',
  'treasury_match_bill',
  'treasury_match_khata',
  'treasury_rails_event',
  'treasury_record_settlement',
  'treasury_refund',
  'treasury_resolve_exception',
  'trust_view',
  'tts_result',
  'turn_request',
  'verdict_view',
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
