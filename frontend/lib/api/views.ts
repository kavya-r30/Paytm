// Every J9 view: query key, path, contract name and the fixture used before a session exists.
// The first query-key segment is the backend's view name, so `view.invalidate {views: ["bill/pay"]}`
// refetches exactly the matching queries.
import type { ContractTypes, LayerPendingView, SchemaName } from '../contracts';
import * as F from '../fixtures/gupta';

export type ViewSpec<T> = {
  key: readonly [string, ...string[]];
  path: string;
  schema: SchemaName | null;
  fixture: () => T | LayerPendingView;
};

function spec<N extends SchemaName>(
  key: readonly [string, ...string[]],
  path: string,
  schema: N,
  fixture: () => ContractTypes[N],
): ViewSpec<ContractTypes[N]> {
  return { key, path, schema, fixture };
}

/** A view whose data arrives with a later layer: the API returns layer_pending_view until then. */
function later(
  key: readonly [string, ...string[]],
  path: string,
  layer: LayerPendingView['layer'],
  reason: string,
): ViewSpec<LayerPendingView> {
  return {
    key,
    path,
    schema: 'layer_pending_view',
    fixture: () => ({
      screen: key[0],
      status: 'not_built_yet',
      layer,
      reason_key: reason,
      items: [],
      invalidate_on: [],
    }),
  };
}

const enc = encodeURIComponent;

export const views = {
  home: () => spec(['home'], '/v1/views/home', 'home_view', () => F.home),
  ask: (session = 'current') =>
    later(['ask', session], `/v1/views/ask?session=${enc(session)}`, 'L4', 'sufficiency.ask_pending'),
  forecast: (metric: 'sales' | 'items' = 'sales') =>
    later(['forecast', metric], `/v1/views/forecast?metric=${metric}`, 'L3', 'sufficiency.forecast_pending'),
  notifications: () =>
    spec(['notifications'], '/v1/views/notifications', 'notifications_view', () => F.notifications),
  gate: (id: string) =>
    spec(
      ['gates', id],
      `/v1/views/gates/${enc(id)}`,
      'gate_view',
      () => F.gates[id] ?? Object.values(F.gates)[0]!,
    ),
  bill: (id: string) =>
    spec(['bill', id], `/v1/views/bill/${enc(id)}`, 'bill_view', () => ({
      ...F.bill,
      bill: { ...F.bill.bill, id },
    })),
  billPay: (id: string) =>
    spec(['bill/pay', id], `/v1/views/bill/${enc(id)}/pay`, 'bill_pay_view', () => ({
      ...F.billPay,
      bill: { ...F.billPay.bill, id },
    })),
  billPaid: (id: string) =>
    spec(['bill/paid', id], `/v1/views/bill/${enc(id)}/paid`, 'bill_paid_view', () => F.billPaid),
  park: () => spec(['park'], '/v1/views/park', 'park_view', () => F.park),
  customers: (q: string) =>
    spec(
      ['customers', q],
      `/v1/views/customers/search${q.trim() ? `?q=${enc(q.trim())}` : ''}`,
      'customer_search_view',
      () => ({
        ...F.customers,
        customers: F.customers.customers.filter((c) =>
          c.display_name.toLowerCase().includes(q.trim().toLowerCase()),
        ),
      }),
    ),
  orders: () => spec(['orders'], '/v1/views/orders', 'orders_view', () => F.orders),
  order: (id: string) => spec(['orders', id], `/v1/views/orders/${enc(id)}`, 'order_view', () => F.order),
  khata: () => spec(['khata'], '/v1/views/khata', 'khata_view', () => F.khata),
  khataAccount: (patronId: string) =>
    spec(
      ['khata', patronId],
      `/v1/views/khata/${enc(patronId)}`,
      'khata_account_view',
      () => F.khataAccounts.find((a) => a.patron_id === patronId) ?? F.khataAccounts[0]!,
    ),
  promises: () => spec(['promises'], '/v1/views/promises', 'promises_view', () => F.promises),
  patron: (id: string) =>
    spec(['patron', id], `/v1/views/patron/${enc(id)}`, 'patron_view', () => F.patron(id)),
  stock: () => spec(['stock'], '/v1/views/stock', 'stock_view', () => F.stock),
  item: (id: string) =>
    spec(['item', id], `/v1/views/item/${enc(id)}`, 'catalog_item_view', () => {
      const it = Object.values(F.ITEMS).find((i) => i.id === id) ?? F.ITEMS.maggi;
      return {
        id: it.id,
        sku: it.name.toUpperCase().replace(/[^A-Z0-9]+/g, '-'),
        names: { en: it.name },
        unit: it.unit,
        price_paise: it.price,
        modifier_groups: [],
        recipe: [],
        invalidate_on: ['catalog.price_changed'],
      };
    }),
  expiry: () => spec(['stock/expiry'], '/v1/views/stock/expiry', 'expiry_view', () => F.expiry),
  suppliers: () => spec(['suppliers'], '/v1/views/suppliers', 'suppliers_view', () => F.suppliers),
  po: (id: string) => spec(['po', id], `/v1/views/po/${enc(id)}`, 'po_view', () => F.po),
  grn: (poId: string) => spec(['grn', poId], `/v1/views/grn/${enc(poId)}`, 'grn_view', () => F.grn),
  claim: (id: string) => spec(['claims', id], `/v1/views/claims/${enc(id)}`, 'claim_view', () => F.claim),
  grow: () => later(['grow'], '/v1/views/grow', 'L6', 'sufficiency.growth_pending'),
  plan: (id: string) =>
    later(['grow/plans', id], `/v1/views/grow/plans/${enc(id)}`, 'L6', 'sufficiency.plan_pending'),
  demand: () => spec(['grow/demand'], '/v1/views/grow/demand', 'demand_view', () => F.demand),
  bundles: () => later(['grow/bundles'], '/v1/views/grow/bundles', 'L6', 'sufficiency.bundles_pending'),
  ledger: () => later(['grow/ledger'], '/v1/views/grow/ledger', 'L6', 'sufficiency.ledger_pending'),
  campaign: (id: string) =>
    later(['campaigns', id], `/v1/views/campaigns/${enc(id)}`, 'L6', 'sufficiency.campaign_pending'),
  offers: () => spec(['offers'], '/v1/views/offers', 'offers_view', () => F.offers),
  offer: (id: string) =>
    spec(['offers', id], `/v1/views/offers/${enc(id)}`, 'offer_detail_view', () => F.offerDetail),
  storefront: () => spec(['storefront'], '/v1/views/storefront', 'storefront_view', () => F.storefront),
  team: () => later(['team'], '/v1/views/team', 'L5', 'sufficiency.team_pending'),
  run: (id: string) => later(['runs', id], `/v1/views/runs/${enc(id)}`, 'L5', 'sufficiency.run_pending'),
  memory: () => later(['memory'], '/v1/views/memory', 'L5', 'sufficiency.memory_pending'),
  hisaab: () => spec(['hisaab'], '/v1/views/hisaab', 'hisaab_view', () => F.hisaab),
  reports: () => spec(['reports'], '/v1/views/reports', 'reports_view', () => F.reports),
  feedback: () => spec(['feedback'], '/v1/views/feedback', 'feedback_view', () => F.feedback),
  language: () =>
    spec(['settings/language'], '/v1/views/settings/language', 'settings_view', () => F.settings),
  staff: () => spec(['settings/staff'], '/v1/views/settings/staff', 'staff_view', () => F.staffView),
  trust: () => spec(['trust'], '/v1/views/trust', 'trust_view', () => F.trust),
  health: () => spec(['health'], '/v1/views/health', 'health_view', () => F.health),
  capital: () => spec(['capital'], '/v1/views/capital', 'capital_view', () => F.capital),
  onboarding: () => spec(['onboarding'], '/v1/views/onboarding', 'onboarding_view', () => F.onboarding),
  staffLogin: () => spec(['staff/login'], '/v1/views/staff/login', 'staff_view', () => F.staffView),
  shift: () => spec(['shift'], '/v1/views/shift', 'shift_view', () => F.shift),
  kot: () => spec(['kot'], '/v1/views/kot', 'kot_view', () => F.kot),
  appointments: (date = '2026-10-29') =>
    spec(
      ['appointments', date],
      `/v1/views/appointments?date=${date}`,
      'appointments_view',
      () => F.appointments,
    ),
  rx: () => spec(['rx'], '/v1/views/rx', 'rx_view', () => F.rx),
  verdict: (id: string) =>
    spec(['verdict', id], `/v1/views/verdict/${enc(id)}`, 'verdict_view', () => F.verdict),
  publicStorefront: (slug: string) =>
    spec(['public/storefront', slug], `/v1/public/storefront/${enc(slug)}`, 'public_storefront', () => ({
      ...F.publicStorefront,
      slug,
    })),
};

export function isPending(data: unknown): data is LayerPendingView {
  return (
    typeof data === 'object' &&
    data !== null &&
    'status' in data &&
    ((data as { status: unknown }).status === 'not_built_yet' ||
      ((data as { status: unknown }).status === 'needs_more_data' && 'layer' in data))
  );
}
