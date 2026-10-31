import { describe, expect, it } from 'vitest';
import { deriveState } from '../lib/customer-display';
import { merchantId } from '../lib/api/sim';
import { SCENARIOS, at, holds } from '../lib/scenarios';
import { CATALOGUES } from '../lib/i18n/core';

const BILL = 'bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0';
const ev = (type: string, payload: Record<string, unknown>) => ({ type, data: { payload } });

describe('customer display (T7.11)', () => {
  it('follows the newest event for the bill', () => {
    expect(deriveState([]).state).toBe('idle');
    expect(deriveState([ev('bill.changed', { bill_id: BILL })])).toEqual({
      state: 'amount',
      billId: BILL,
      amount: null,
    });
    expect(
      deriveState([ev('payment.pending', { bill_id: BILL }), ev('bill.changed', { bill_id: BILL })]).state,
    ).toBe('pending');
    expect(deriveState([ev('bill.paid', { bill_id: BILL, total_paise: 9000 })]).amount).toBe(9000);
    expect(
      deriveState([ev('offer.issued', { amount_paise: 2500 }), ev('bill.paid', { bill_id: BILL })]).state,
    ).toBe('reward');
  });
  it('ignores events it does not show (no khata or hint leakage)', () => {
    expect(deriveState([ev('credit.changed', { balance_paise: 500 }), ev('hint.offered', {})]).state).toBe(
      'idle',
    );
  });
});

describe('director (T7.16)', () => {
  it('reads the merchant from a session token', () => {
    expect(merchantId(`mer_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0.session_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1.session.abc`)).toBe(
      'mer_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0',
    );
    expect(merchantId('garbage')).toBeNull();
    expect(merchantId(null)).toBeNull();
  });
  it('evaluates beat expectations like the backend runner', () => {
    const body = { today: { sales_paise: 12000 }, audit: { ok: true } };
    expect(at(body, 'today.sales_paise')).toBe(12000);
    expect(holds(body, { view: 'hisaab', path: 'today.sales_paise', gte: 9000 })).toBe(true);
    expect(holds(body, { view: 'trust', path: 'audit.ok', equals: true })).toBe(true);
    expect(holds(body, { view: 'trust', path: 'audit.missing', equals: true })).toBe(false);
  });
  it('every beat has a title and cue in English', () => {
    for (const s of SCENARIOS) {
      expect(CATALOGUES.en[s.title_key]).toBeDefined();
      for (const b of s.beats) {
        expect(CATALOGUES.en[b.title_key], b.id).toBeDefined();
        expect(CATALOGUES.en[b.cue_key], b.id).toBeDefined();
      }
    }
  });
});
