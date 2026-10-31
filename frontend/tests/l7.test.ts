import { describe, expect, it } from 'vitest';
import { CARD_TYPES, audiencesFor, cardsFor } from '../lib/cards';
import { offlineAllowed } from '../lib/api/journal';
import { SseParser, invalidatedViews } from '../lib/api/stream';
import { views } from '../lib/api/views';
import { IDS } from '../lib/fixtures/gupta';
import { CATALOGUES, fitSize, lookup, pseudoize, qty, translate, UI_LOCALES } from '../lib/i18n/core';
import { INTENTS, resolveIntent } from '../lib/voice/intents';
import { validate, validator } from '../lib/validate';
import { SCREENS } from '../screens/device/registry';

const ID = 'x_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0';

describe('fixtures (T7.4): every fixture view is valid against its contract', () => {
  const specs = [
    views.home(),
    views.notifications(),
    views.gate(IDS.GATES.po.gate),
    views.gate(IDS.GATES.reminder.gate),
    views.bill(IDS.BILL_ID),
    views.billPay(IDS.BILL_ID),
    views.billPaid(IDS.PAID_BILL_ID),
    views.park(),
    views.customers('pr'),
    views.orders(),
    views.order('o'),
    views.khata(),
    views.khataAccount('p'),
    views.promises(),
    views.patron('p'),
    views.stock(),
    views.item('i'),
    views.expiry(),
    views.suppliers(),
    views.po('p'),
    views.grn('p'),
    views.claim('c'),
    views.demand(),
    views.offers(),
    views.offer('o'),
    views.storefront(),
    views.hisaab(),
    views.reports(),
    views.feedback(),
    views.language(),
    views.staff(),
    views.trust(),
    views.health(),
    views.capital(),
    views.onboarding(),
    views.shift(),
    views.kot(),
    views.appointments(),
    views.rx(),
    views.verdict('v'),
    views.publicStorefront('gupta-general-store'),
    views.ask(),
    views.forecast(),
    views.grow(),
    views.team(),
    views.memory(),
    views.plan('p'),
    views.campaign('c'),
    views.ledger(),
    views.bundles(),
    views.run('r'),
  ];
  for (const spec of specs) {
    it(`${spec.path} → ${spec.schema}`, () => {
      const data = spec.fixture();
      const ok = validate(spec.schema!, data);
      expect(ok, JSON.stringify(validator(spec.schema!).errors)).toBe(true);
    });
  }
});

describe('i18n (T7.2)', () => {
  it('every locale catalogue only uses keys English defines', () => {
    for (const [locale, cat] of Object.entries(CATALOGUES)) {
      const extra = Object.keys(cat).filter((k) => !(k in CATALOGUES.en));
      expect(extra, locale).toEqual([]);
    }
  });
  it('falls back along the chain: mr → hi → en', () => {
    expect(lookup('mr', 'nav.home')).toBe('आज');
    expect(lookup('mr', 'khata.send_reminder')).toBe(CATALOGUES.hi['khata.send_reminder']);
    expect(lookup('ta', 'reports.gst')).toBe('GST');
  });
  it('formats ICU params and leaves unknown keys visible', () => {
    expect(translate('en', 'home.batch_title', { n: 3 })).toBe('One yes, 3 jobs');
    expect(translate('hi-Latn', 'home.batch_title', { n: 3 })).toBe('Aapka ek haan, 3 kaam');
    expect(translate('en', 'no.such_key')).toBe('Such key'); // a gap reads as words, never a raw key
    expect(translate('en', 'error.policy.consent')).toMatch(/agreed/); // refusals read as sentences
  });
  it('pseudo-locale is ≥40% longer, accented, and keeps placeholders', () => {
    const p = translate('xx-LONG', 'home.batch_title', { n: 3 });
    expect(p.length).toBeGreaterThanOrEqual(Math.ceil('One yes, 3 jobs'.length * 1.4));
    expect(p).toContain('3');
    expect(pseudoize('Save {n}')).toContain('{n}');
    expect(UI_LOCALES).toContain('xx-LONG');
  });
  it('text fit shrinks to the box but not below min', () => {
    expect(fitSize(100, 200, 56, 32)).toBe(56);
    expect(fitSize(400, 200, 56, 32)).toBe(32);
    expect(fitSize(300, 200, 56, 20)).toBe(37);
    expect(qty(500)).toBe('0.5');
    expect(qty(2000)).toBe('2');
  });
});

describe('card registry (T7.5, SRF-1/SRF-4)', () => {
  it('the customer display never renders owner cards', () => {
    const envelope = {
      audience: 'all' as const,
      cards: CARD_TYPES.flatMap((type) => [
        { type, audience: 'all' as const },
        { type, audience: 'owner' as const },
        { type },
      ]),
    };
    const shown = cardsFor('customer', envelope);
    expect(shown.length).toBeGreaterThan(0);
    for (const card of shown) {
      expect(card.audience).not.toBe('owner');
      expect(audiencesFor(card.type)).toContain('customer');
    }
    expect(shown.some((c) => c.type === 'hint')).toBe(false);
  });
  it('an owner-audience envelope shows nothing on the customer display', () => {
    expect(cardsFor('customer', { audience: 'owner', cards: [{ type: 'bill' }] })).toEqual([]);
    expect(cardsFor('owner', { audience: 'owner', cards: [{ type: 'hint' }] })).toHaveLength(1);
  });
});

describe('data layer (T7.4)', () => {
  it('parses SSE across chunk boundaries', () => {
    const p = new SseParser();
    expect(p.feed('event: view.invalidate\nid: 1\ndata: {"payload":')).toEqual([]);
    const msgs = p.feed('{"views":["home","bill/pay"]}}\n\n: ping\n\n');
    expect(msgs).toHaveLength(1);
    expect(msgs[0]!.event).toBe('view.invalidate');
    expect(invalidatedViews(JSON.parse(msgs[0]!.data))).toEqual(['home', 'bill/pay']);
  });
  it('query keys start with the backend view name so invalidation matches', () => {
    expect(views.billPay(ID).key[0]).toBe('bill/pay');
    expect(views.expiry().key[0]).toBe('stock/expiry');
    expect(views.language().key[0]).toBe('settings/language');
  });
  it('only cash/static-QR counter work is journalled offline (EDG-1)', () => {
    expect(offlineAllowed('counter.add_lines', {})).toBe(true);
    expect(offlineAllowed('counter.checkout', { mode: 'cash' })).toBe(true);
    expect(offlineAllowed('counter.checkout', { mode: 'upi' })).toBe(false);
    expect(offlineAllowed('ledger.send_reminder', {})).toBe(false);
  });
});

describe('voice parity (T7.17, A11Y-1)', () => {
  it('every device screen has at least one utterance', () => {
    const reachable = new Set(INTENTS.map((i) => i.screen?.split('/')[0]).filter(Boolean));
    const missing = Object.keys(SCREENS).filter(
      (s) => !reachable.has(s) && !['pay', 'paid', 'offer', 'order'].includes(s),
    );
    expect(missing).toEqual([]);
  });
  it('resolves the spec examples', () => {
    expect(resolveIntent('Sharma ji ka hisaab')?.screen).toBe('khata');
    expect(resolveIntent('Teeno haan')?.action).toBe('approve_all');
    expect(resolveIntent('QR dikhao')?.action).toBe('show_qr');
    expect(resolveIntent('Kya khatam hone wala hai?')?.screen).toBe('stock');
    expect(resolveIntent('Kal kitni bikri hogi?')?.screen).toBe('forecast');
    expect(resolveIntent('naya bill')?.screen).toBe('bill/new');
  });
});
