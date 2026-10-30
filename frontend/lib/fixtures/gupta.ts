// Gupta General Store fixture shop (demo scenario 1), shaped exactly like the live views so every screen
// renders before the seeded shop exists. tests/fixtures.test.ts validates each entry against its contract.
import type {
  AppointmentsView,
  BillPaidView,
  BillPayView,
  BillView,
  CapitalView,
  ClaimView,
  CustomerSearchView,
  DemandView,
  ExpiryView,
  FeedbackView,
  GateView,
  GrnView,
  HealthView,
  HisaabView,
  HomeView,
  KhataAccountView,
  KhataView,
  KotView,
  NotificationsView,
  OfferDetailView,
  OffersView,
  OnboardingView,
  OrderView,
  OrdersView,
  ParkView,
  PatronView,
  PoView,
  PromisesView,
  PublicStorefront,
  ReportsView,
  RxView,
  SettingsView,
  ShiftView,
  StaffView,
  StockView,
  StorefrontView,
  SuppliersView,
  TrustView,
  VerdictView,
} from '../contracts';
import { NOW, fid, minutesAgo, minutesAhead } from './ids';

const INV = (...topics: string[]) => topics;

export const ITEMS = {
  maggi: { id: fid('item', 1), name: 'Maggi 70 g', price: 1400, unit: 'pcs', cat: 'aksar', icon: 'noodles' },
  parle: { id: fid('item', 2), name: 'Parle-G', price: 1000, unit: 'pcs', cat: 'aksar', icon: 'biscuit' },
  amul: {
    id: fid('item', 3),
    name: 'Amul Taaza 500 ml',
    price: 2800,
    unit: 'pcs',
    cat: 'dairy',
    icon: 'milk',
  },
  salt: {
    id: fid('item', 4),
    name: 'Tata Salt 1 kg',
    price: 2800,
    unit: 'pcs',
    cat: 'staples',
    icon: 'salt',
  },
  atta: { id: fid('item', 5), name: 'Atta 5 kg', price: 26500, unit: 'pcs', cat: 'staples', icon: 'sack' },
  sugar: { id: fid('item', 6), name: 'Sugar, loose', price: 4800, unit: 'kg', cat: 'staples', icon: 'sack' },
  oil: { id: fid('item', 7), name: 'Oil 1 L', price: 16500, unit: 'pcs', cat: 'staples', icon: 'oil' },
  tea: { id: fid('item', 8), name: 'Tea 250 g', price: 14000, unit: 'pcs', cat: 'aksar', icon: 'tea' },
  ghee: { id: fid('item', 9), name: 'Ghee 1 L', price: 65000, unit: 'pcs', cat: 'diwali', icon: 'oil' },
  kaju: { id: fid('item', 10), name: 'Kaju 1 kg', price: 98000, unit: 'kg', cat: 'diwali', icon: 'nut' },
  dahi: { id: fid('item', 11), name: 'Dahi 400 g', price: 3500, unit: 'pcs', cat: 'dairy', icon: 'milk' },
  besan: { id: fid('item', 12), name: 'Besan 1 kg', price: 11000, unit: 'kg', cat: 'diwali', icon: 'sack' },
} as const;
export type FixtureItem = (typeof ITEMS)[keyof typeof ITEMS];

export const PATRONS = {
  priya: { id: fid('pat', 1), name: 'Priya Verma', phone: '98•••••210', lang: 'hi' },
  mehta: { id: fid('pat', 2), name: 'Mehta ji', phone: '98•••••114', lang: 'hi-Latn' },
  sharma: { id: fid('pat', 3), name: 'Sharma ji', phone: '99•••••871', lang: 'hi' },
  sunita: { id: fid('pat', 4), name: 'Sunita ji', phone: '97•••••452', lang: 'hi' },
  rohit: { id: fid('pat', 5), name: 'Rohit Kumar', phone: '88•••••309', lang: 'en' },
} as const;

export const SUPPLIERS = {
  balaji: { id: fid('supplier', 1), name: 'Balaji Traders' },
  agarwal: { id: fid('supplier', 2), name: 'Agarwal Traders' },
} as const;

export const STAFF = {
  ramesh: { id: fid('staff', 1), name: 'Ramesh Gupta', role: 'owner' as const },
  raju: { id: fid('staff', 2), name: 'Raju', role: 'cashier' as const },
  chotu: { id: fid('staff', 3), name: 'Chotu', role: 'helper' as const },
};

/** Display names for IDs the views carry without names (contract-change request #2). */
export const NAMES: Record<string, string> = Object.fromEntries([
  ...Object.values(ITEMS).map((i) => [i.id, i.name]),
  ...Object.values(PATRONS).map((p) => [p.id, p.name]),
  ...Object.values(SUPPLIERS).map((s) => [s.id, s.name]),
  ...Object.values(STAFF).map((s) => [s.id, s.name]),
]);

const BILL_ID = fid('bill', 42);
const PAID_BILL_ID = fid('bill', 41);
const PO_ID = fid('po', 1);
const CLAIM_ID = fid('claim', 1);
const GATES = {
  reminder: { gate: fid('gate', 1), thread: fid('thread', 1), type: 'ledger.send_reminder' },
  po: { gate: fid('gate', 2), thread: fid('thread', 2), type: 'supply.place_po' },
  winback: { gate: fid('gate', 3), thread: fid('thread', 3), type: 'growth.launch_campaign' },
};

function line(id: number, item: FixtureItem, qtyMilli: number, via: string) {
  return {
    id: fid('bline', id),
    item_id: item.id,
    name: item.name,
    qty_milli: qtyMilli,
    unit_price_paise: item.price,
    amount_paise: Math.round((item.price * qtyMilli) / 1000),
    added_via: via,
    modifier_ids: [],
    price_override: false,
    batch_id: null,
  };
}

const openLines = [
  line(1, ITEMS.maggi, 2000, 'scanned'),
  line(2, ITEMS.sugar, 500, 'voice'),
  line(3, ITEMS.parle, 1000, 'voice'),
];
const openTotal = openLines.reduce((s, l) => s + l.amount_paise, 0);

const openBill: BillView['bill'] = {
  id: BILL_ID,
  status: 'open',
  patron_id: PATRONS.priya.id,
  staff_id: STAFF.ramesh.id,
  opened_at: minutesAgo(3),
  closed_at: null,
  total_paise: openTotal,
  paid_paise: 0,
  khata_paise: 0,
  due_paise: openTotal,
  lines: openLines,
  payments: [],
  ticket: null,
  upi: null,
  patron: {
    id: PATRONS.priya.id,
    display_name: PATRONS.priya.name,
    lang: 'hi',
    khata_balance_paise: 0,
    reward_stamps: 3,
  },
};

const paidLines = [...openLines, line(4, ITEMS.amul, 1000, 'tapped')];
const paidTotal = paidLines.reduce((s, l) => s + l.amount_paise, 0);

/** Gate summaries as the backend computes them: title_key = "gate." + type, params from the scope. */
const SUMMARY: Record<string, Record<string, string | number | null>> = {
  [GATES.reminder.gate]: { patron: PATRONS.mehta.name, amount_paise: 215000 },
  [GATES.po.gate]: { supplier: SUPPLIERS.balaji.name, amount_paise: 1840000 },
  [GATES.winback.gate]: { amount_paise: 12500 },
};

function gateRow(
  g: { gate: string; thread: string; type: string },
  tier: 'R2' | 'R3',
  expires: string,
  status = 'pending',
) {
  return {
    gate_id: g.gate,
    thread_id: g.thread,
    tier,
    type: g.type,
    status,
    expires_at: expires,
    title_key: `gate.${g.type.replace(/\./g, '_')}`,
    summary_params: SUMMARY[g.gate] ?? {},
  };
}

const gateRows = [
  gateRow(GATES.reminder, 'R3', minutesAhead(600)),
  gateRow(GATES.po, 'R3', minutesAhead(240)),
  gateRow(GATES.winback, 'R3', minutesAhead(900)),
];

export const home: HomeView = {
  greeting: { owner_name: 'Ramesh', shop_name: 'Gupta General Store', now: NOW, part_of_day: 'midday' },
  today: {
    sales_paise: 418000,
    bills: 31,
    customers: 38,
    new_customers: 6,
    by_mode: { upi: 326000, cash: 66900, khata: 25100 },
  },
  khata: { outstanding_paise: 501000, change_today_paise: -50000 },
  gates: gateRows,
  brief: {
    text: 'Dopahar tak ₹4,180, aam guruvaar se 13% aage. Shaam 6–8 sabse zyada bheed hogi, doodh aur Maggi pehle se aage rakh lijiye.',
    duration_s: 14,
    delta_bp: 1300,
    intraday: {
      hours: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
      today: [0, 30000, 70000, 190000, 260000, 330000, 418000],
      typical: [
        0, 25000, 60000, 120000, 190000, 270000, 370000, 450000, 520000, 600000, 700000, 780000, 840000,
        880000, 900000,
      ],
      band_low: [
        null,
        null,
        null,
        null,
        null,
        null,
        418000,
        480000,
        560000,
        650000,
        760000,
        850000,
        900000,
        920000,
        930000,
      ],
      band_high: [
        null,
        null,
        null,
        null,
        null,
        null,
        418000,
        520000,
        620000,
        730000,
        850000,
        940000,
        990000,
        1020000,
        1040000,
      ],
      pin: {
        hour: 11,
        amount_paise: 124000,
        note: '11:20 · ₹1,240 Mehta ji ka Diwali order. Isliye aage hain.',
      },
    },
  },
  data_sufficiency: { status: 'ready', days_of_history: 412, reason_key: 'sufficiency.history_days' },
  invalidate_on: INV('bill.paid', 'bill.changed', 'payment.received', 'approval.requested', 'credit.changed'),
};

export const notifications: NotificationsView = {
  needs_you: gateRows,
  done: [
    {
      command_id: fid('cmd', 1),
      type: 'ledger.send_statement',
      tier: 'R1',
      occurred_at: minutesAgo(1),
      undo_until: minutesAhead(0.4),
    },
    {
      command_id: fid('cmd', 2),
      type: 'stock.count',
      tier: 'R1',
      occurred_at: minutesAgo(45),
      undo_until: null,
    },
    {
      command_id: fid('cmd', 3),
      type: 'treasury.match_bill',
      tier: 'R0',
      occurred_at: minutesAgo(130),
      undo_until: null,
    },
  ],
  snoozed: [
    gateRow(
      { gate: fid('gate', 4), thread: fid('thread', 4), type: 'catalog.change_price' },
      'R2',
      minutesAhead(180),
      'snoozed',
    ),
  ],
  invalidate_on: INV('approval.requested', 'approval.decided', 'command.executed'),
};

export const gates: Record<string, GateView> = {
  [GATES.po.gate]: {
    gate: {
      gate_id: GATES.po.gate,
      thread_id: GATES.po.thread,
      tier: 'R3',
      type: 'supply.place_po',
      status: 'pending',
      expires_at: minutesAhead(240),
      title_key: 'gate.supply_place_po',
      summary_params: { supplier: SUPPLIERS.balaji.name, amount_paise: 1840000 },
      scope: {
        type: 'supply.place_po',
        payload: {
          supplier_id: SUPPLIERS.balaji.id,
          total_paise: 1840000,
          saving_paise: 85000,
          quotes: [
            {
              supplier_id: SUPPLIERS.balaji.id,
              total_paise: 1840000,
              credit_days: 15,
              delivery: 'kal subah',
              reliability_bp: 9400,
              recommended: true,
            },
            {
              supplier_id: SUPPLIERS.agarwal.id,
              total_paise: 1925000,
              credit_days: 7,
              delivery: 'parso',
              reliability_bp: 8100,
              recommended: false,
            },
          ],
          lines: [
            { item_id: ITEMS.kaju.id, qty_milli: 5000, unit_price_paise: 92000 },
            { item_id: ITEMS.ghee.id, qty_milli: 12000, unit_price_paise: 61000 },
            { item_id: ITEMS.besan.id, qty_milli: 20000, unit_price_paise: 10200 },
          ],
          note: 'Balaji ₹850 sasta hai aur pichhle 6 orders mein time pe aaya. Agarwal ka credit kam hai.',
          budget_left_paise: 660000,
        },
      },
      conditions: { max_unit_price_paise: { [ITEMS.kaju.id]: 92000 } },
    },
    readback_key: null,
    invalidate_on: INV('approval.decided', 'approval.requested', 'message.in'),
  },
  [GATES.reminder.gate]: {
    gate: {
      gate_id: GATES.reminder.gate,
      thread_id: GATES.reminder.thread,
      tier: 'R3',
      type: 'ledger.send_reminder',
      status: 'pending',
      expires_at: minutesAhead(600),
      title_key: 'gate.ledger_send_reminder',
      summary_params: { patron: PATRONS.mehta.name, amount_paise: 215000 },
      scope: {
        type: 'ledger.send_reminder',
        payload: {
          patron_id: PATRONS.mehta.id,
          amount_paise: 215000,
          send_at: '2026-10-30T03:30:00Z',
          draft:
            'Namaste Mehta ji, Gupta General Store se. Aapka ₹2,150 baaki hai. Suvidha ho to is link se de dijiye. Dhanyavaad!',
        },
      },
      conditions: {},
    },
    readback_key: null,
    invalidate_on: INV('approval.decided'),
  },
  [GATES.winback.gate]: {
    gate: {
      gate_id: GATES.winback.gate,
      thread_id: GATES.winback.thread,
      tier: 'R3',
      type: 'growth.launch_campaign',
      status: 'pending',
      expires_at: minutesAhead(900),
      title_key: 'gate.growth_launch_campaign',
      summary_params: { amount_paise: 12500 },
      scope: {
        type: 'growth.launch_campaign',
        payload: { audience: 5, treated: 4, holdout: 1, budget_paise: 12500, lever: 'winback' },
      },
      conditions: {},
    },
    readback_key: null,
    invalidate_on: INV('approval.decided'),
  },
};

export const bill: BillView = {
  bill: openBill,
  parked_count: 1,
  invalidate_on: INV('bill.changed', 'bill.paid'),
  quick_items: Object.values(ITEMS).map((i) => ({
    item_id: i.id,
    name: i.name,
    price_paise: i.price,
    unit: i.unit,
    category: i.cat,
  })),
  categories: [
    { key: 'aksar', label: 'Aksar' },
    { key: 'dairy', label: 'Doodh, dahi' },
    { key: 'staples', label: 'Atta, chawal' },
    { key: 'diwali', label: 'Diwali' },
  ],
};

export const billPay: BillPayView = {
  bill: {
    ...openBill,
    upi: { order_ref: 'UPI-1042', amount_paise: openTotal, status: 'waiting', expires_at: minutesAhead(4) },
  },
  payee_vpa: 'guptastore@paytm',
  alternatives: ['cash', 'khata'],
  exception: null,
  invalidate_on: INV('payment.received', 'bill.paid'),
};

export const billPaid: BillPaidView = {
  bill: {
    ...openBill,
    id: PAID_BILL_ID,
    status: 'closed',
    closed_at: minutesAgo(1),
    lines: paidLines,
    total_paise: paidTotal,
    paid_paise: paidTotal,
    due_paise: 0,
    payments: [{ mode: 'upi', amount_paise: paidTotal, change_paise: null, ref_id: 'UTR629104882713' }],
  },
  invoice: null,
  receipt: { status: 'queued', lang: 'hi' },
  offers: [
    {
      issuance_id: fid('issue', 1),
      kind: 'next_txn_cashback',
      amount_paise: 2500,
      min_spend_paise: 50000,
      expires_at: '2026-11-12T00:00:00Z',
      code: null,
    },
  ],
  utr_tail: '2713',
  invalidate_on: INV('payment.received', 'offer.issued'),
};

export const park: ParkView = {
  bills: [
    {
      id: fid('bill', 39),
      patron_id: PATRONS.sunita.id,
      patron_name: PATRONS.sunita.name,
      total_paise: 34500,
      lines: 4,
      opened_at: minutesAgo(22),
    },
  ],
  invalidate_on: INV('bill.changed'),
};

export const customers: CustomerSearchView = {
  customers: Object.values(PATRONS).map((p, i) => ({
    patron_id: p.id,
    display_name: p.name,
    confidence: 1 - i * 0.05,
  })),
  needs_clarification: false,
  invalidate_on: INV('patron.changed', 'patron.merged'),
  recent: Object.values(PATRONS).map((p) => ({
    patron_id: p.id,
    display_name: p.name,
    phone_masked: p.phone,
    khata_balance_paise: null,
    reward_stamps: p.id === PATRONS.priya.id ? 3 : 1,
  })),
};

function account(
  n: number,
  patron: (typeof PATRONS)[keyof typeof PATRONS],
  entries: { amount: number; ago: number; items?: [FixtureItem, number][] }[],
  payments: { amount: number; ago: number }[],
  limit = 500000,
): KhataAccountView {
  const entriesPaise = entries.reduce((s, e) => s + e.amount, 0);
  const paid = payments.reduce((s, p) => s + p.amount, 0);
  return {
    account_id: fid('account', n),
    as_of: NOW,
    entries: entries.map((e, i) => ({
      id: fid('entry', n * 10 + i),
      account_id: fid('account', n),
      amount_paise: e.amount,
      source: 'counter',
      ref_id: null,
      member_id: null,
      reversal_of: null,
      occurred_at: minutesAgo(e.ago),
      status: 'open',
      allocated_paise: 0,
      lines: (e.items ?? []).map(([item, q]) => ({
        item_id: item.id,
        description_key: null,
        qty_milli: q,
        unit_price_paise: item.price,
        amount_paise: Math.round((item.price * q) / 1000),
      })),
    })),
    payments: payments.map((p, i) => ({
      payment_ref: fid('pay', n * 10 + i),
      amount_paise: p.amount,
      mode: 'upi',
      occurred_at: minutesAgo(p.ago),
    })),
    entries_paise: entriesPaise,
    allocated_paise: paid,
    balance_paise: entriesPaise - paid,
    advance_paise: 0,
    invalidate_on: INV('credit.changed'),
    patron_id: patron.id,
    display_name: patron.name,
    limit_paise: limit,
    promises: [],
    pay_link_ref: null,
  };
}

const DAY = 24 * 60;
export const khataAccounts: KhataAccountView[] = [
  account(
    1,
    PATRONS.sharma,
    [
      {
        amount: 120000,
        ago: 18 * DAY,
        items: [
          [ITEMS.atta, 2000],
          [ITEMS.oil, 3000],
          [ITEMS.sugar, 4000],
        ],
      },
      {
        amount: 95000,
        ago: 9 * DAY,
        items: [
          [ITEMS.ghee, 1000],
          [ITEMS.tea, 2000],
        ],
      },
    ],
    [{ amount: 50000, ago: 2 * DAY }],
  ),
  account(
    2,
    PATRONS.mehta,
    [
      {
        amount: 215000,
        ago: 26 * DAY,
        items: [
          [ITEMS.kaju, 1000],
          [ITEMS.ghee, 1000],
          [ITEMS.atta, 2000],
        ],
      },
    ],
    [],
  ),
  account(
    3,
    PATRONS.sunita,
    [
      {
        amount: 68000,
        ago: 6 * DAY,
        items: [
          [ITEMS.amul, 10000],
          [ITEMS.dahi, 4000],
          [ITEMS.parle, 6000],
        ],
      },
    ],
    [],
  ),
  account(
    4,
    PATRONS.rohit,
    [
      {
        amount: 53000,
        ago: 3 * DAY,
        items: [
          [ITEMS.oil, 2000],
          [ITEMS.tea, 1000],
          [ITEMS.maggi, 6000],
        ],
      },
    ],
    [],
  ),
];
khataAccounts[0]!.promises.push({
  id: fid('promise', 1),
  amount_paise: 165000,
  due_on: '2026-11-01',
  occurred_at: minutesAgo(2 * DAY),
  status: 'active',
});

export const khata: KhataView = {
  accounts: khataAccounts,
  balance_paise: khataAccounts.reduce((s, a) => s + a.balance_paise, 0),
  advance_paise: 0,
  invalidate_on: INV('credit.changed'),
};

export const promises: PromisesView = {
  promises: [
    {
      id: fid('promise', 1),
      account_id: fid('account', 1),
      amount_paise: 165000,
      due_on: '2026-11-01',
      status: 'active',
    },
    {
      id: fid('promise', 2),
      account_id: fid('account', 3),
      amount_paise: 30000,
      due_on: '2026-10-25',
      status: 'kept',
    },
  ],
  invalidate_on: INV('credit.changed'),
};

export function patron(id: string): PatronView {
  const p = Object.values(PATRONS).find((x) => x.id === id) ?? PATRONS.priya;
  return {
    patron_id: p.id,
    display_name: p.name,
    lang: p.lang,
    consent: { marketing: p.id === PATRONS.priya.id, reminders: true, receipts: true },
    household_members:
      p.id === PATRONS.sharma.id ? [{ id: fid('pat', 9), display_name: 'Sharma ji (beta)' }] : [],
    rewards: { stamps: 3, available_rewards: 0, available_value_paise: 0 },
    invalidate_on: INV('patron.changed'),
  };
}

const STOCK_TARGET: Record<string, number> = {
  [ITEMS.kaju.id]: 6000,
  [ITEMS.ghee.id]: 15000,
  [ITEMS.sugar.id]: 50000,
  [ITEMS.maggi.id]: 48000,
  [ITEMS.amul.id]: 24000,
  [ITEMS.atta.id]: 20000,
  [ITEMS.parle.id]: 60000,
  [ITEMS.oil.id]: 12000,
};

function batch(n: number, item: FixtureItem, qty: number, expires: string | null) {
  return {
    id: fid('batch', n),
    batch_no: `B${2600 + n}`,
    expires_on: expires,
    mrp_paise: item.price,
    cost_paise: Math.round(item.price * 0.86),
    recalled: false,
    qty_milli: qty,
  };
}

export const stock: StockView = {
  items: [
    { item: ITEMS.kaju, qty: 1200, exp: '2027-03-01' },
    { item: ITEMS.ghee, qty: 3000, exp: '2027-01-15' },
    { item: ITEMS.sugar, qty: 18000, exp: null },
    { item: ITEMS.maggi, qty: 24000, exp: '2027-04-10' },
    { item: ITEMS.amul, qty: 9000, exp: '2026-10-31' },
    { item: ITEMS.atta, qty: 14000, exp: '2026-12-20' },
    { item: ITEMS.parle, qty: 60000, exp: '2027-02-01' },
    { item: ITEMS.oil, qty: 11000, exp: '2027-05-01' },
  ].map(({ item, qty, exp }, i) => {
    const target = STOCK_TARGET[item.id] ?? qty;
    const cover = qty / target;
    return {
      item_id: item.id,
      on_hand_qty_milli: qty,
      sellable_qty_milli: qty,
      batches: [batch(i + 1, item, qty, exp)],
      name: item.name,
      unit: item.unit,
      category: item.cat,
      target_qty_milli: target,
      status: cover <= 0.05 ? ('out' as const) : cover < 0.35 ? ('low' as const) : ('ok' as const),
      supplier_name: SUPPLIERS.balaji.name,
    };
  }),
  invalidate_on: INV('stock.changed', 'batch.recalled'),
};

export const expiry: ExpiryView = {
  batches: [
    {
      batch_id: fid('batch', 5),
      item_id: ITEMS.amul.id,
      name: ITEMS.amul.name,
      batch_no: 'B2605',
      days_to_expiry: 2,
      recalled: false,
      qty_milli: 9000,
    },
    {
      batch_id: fid('batch', 6),
      item_id: ITEMS.atta.id,
      name: ITEMS.atta.name,
      batch_no: 'B2606',
      days_to_expiry: 52,
      recalled: false,
      qty_milli: 14000,
    },
    {
      batch_id: fid('batch', 2),
      item_id: ITEMS.ghee.id,
      name: ITEMS.ghee.name,
      batch_no: 'B2602',
      days_to_expiry: 78,
      recalled: false,
      qty_milli: 3000,
    },
  ],
  invalidate_on: INV('stock.changed', 'batch.recalled', 'clock.day'),
};

export const suppliers: SuppliersView = {
  suppliers: [
    {
      id: SUPPLIERS.balaji.id,
      name: SUPPLIERS.balaji.name,
      lang: 'hi',
      lead_days: 1,
      open_pos: 1,
      payable_paise: 420000,
    },
    {
      id: SUPPLIERS.agarwal.id,
      name: SUPPLIERS.agarwal.name,
      lang: 'hi',
      lead_days: 2,
      open_pos: 0,
      payable_paise: 0,
    },
  ],
  invalidate_on: INV('po.changed'),
};

export const po: PoView = {
  po: {
    id: PO_ID,
    supplier_id: SUPPLIERS.balaji.id,
    supplier_name: SUPPLIERS.balaji.name,
    status: 'placed',
    total_paise: 1840000,
    due_on: '2026-10-30',
    created_at: minutesAgo(90),
    lines: [
      {
        item_id: ITEMS.kaju.id,
        name: ITEMS.kaju.name,
        qty_milli: 5000,
        unit_price_paise: 92000,
        amount_paise: 460000,
        last_price_paise: 95000,
      },
      {
        item_id: ITEMS.ghee.id,
        name: ITEMS.ghee.name,
        qty_milli: 12000,
        unit_price_paise: 61000,
        amount_paise: 732000,
        last_price_paise: 62000,
      },
      {
        item_id: ITEMS.besan.id,
        name: ITEMS.besan.name,
        qty_milli: 20000,
        unit_price_paise: 10200,
        amount_paise: 204000,
        last_price_paise: null,
      },
      {
        item_id: ITEMS.sugar.id,
        name: ITEMS.sugar.name,
        qty_milli: 50000,
        unit_price_paise: 4440,
        amount_paise: 222000,
        last_price_paise: 4500,
      },
      {
        item_id: ITEMS.oil.id,
        name: ITEMS.oil.name,
        qty_milli: 15000,
        unit_price_paise: 14800,
        amount_paise: 222000,
        last_price_paise: 15000,
      },
    ],
  },
  price_history: [],
  invalidate_on: INV('po.changed'),
};

export const grn: GrnView = {
  po_id: PO_ID,
  supplier_name: SUPPLIERS.balaji.name,
  received: [
    { item_id: ITEMS.kaju.id, qty_milli: 5000, batch_id: null },
    { item_id: ITEMS.sugar.id, qty_milli: 49000, batch_id: null },
  ],
  billed: [
    { item_id: ITEMS.kaju.id, qty_milli: 5000, unit_price_paise: 92000 },
    { item_id: ITEMS.sugar.id, qty_milli: 50000, unit_price_paise: 4440 },
  ],
  variances: [
    {
      item_id: ITEMS.sugar.id,
      name: ITEMS.sugar.name,
      kind: 'qty',
      expected: 50000,
      actual: 49000,
      delta_paise: 4440,
    },
  ],
  claim_id: CLAIM_ID,
  invalidate_on: INV('po.changed', 'stock.changed'),
};

export const claim: ClaimView = {
  claim: {
    id: CLAIM_ID,
    po_id: PO_ID,
    supplier_id: SUPPLIERS.balaji.id,
    amount_paise: 4440,
    status: 'draft',
    lang: 'hi',
    created_at: minutesAgo(10),
  },
  variances: [
    {
      item_id: ITEMS.sugar.id,
      name: ITEMS.sugar.name,
      kind: 'qty',
      expected: 50000,
      actual: 49000,
      delta_paise: 4440,
    },
  ],
  supplier_name: SUPPLIERS.balaji.name,
  invalidate_on: INV('po.changed'),
};

export const orders: OrdersView = {
  orders: [
    {
      id: fid('order', 1),
      status: 'draft',
      channel: 'whatsapp',
      patron_id: PATRONS.mehta.id,
      patron_name: PATRONS.mehta.name,
      total_paise: 124000,
      created_at: minutesAgo(8),
      lines: 5,
    },
    {
      id: fid('order', 2),
      status: 'placed',
      channel: 'storefront',
      patron_id: PATRONS.rohit.id,
      patron_name: PATRONS.rohit.name,
      total_paise: 46500,
      created_at: minutesAgo(50),
      lines: 3,
    },
    {
      id: fid('order', 3),
      status: 'placed',
      channel: 'preorder',
      patron_id: PATRONS.priya.id,
      patron_name: PATRONS.priya.name,
      total_paise: 54900,
      created_at: minutesAgo(200),
      lines: 1,
    },
  ],
  by_status: { draft: 1, placed: 2 },
  invalidate_on: INV('order.changed'),
};

export const order: OrderView = {
  order: {
    id: fid('order', 1),
    status: 'draft',
    channel: 'whatsapp',
    patron_id: PATRONS.mehta.id,
    patron_name: PATRONS.mehta.name,
    total_paise: 124000,
    created_at: minutesAgo(8),
    lines: [
      {
        id: fid('oline', 1),
        item_id: ITEMS.kaju.id,
        text: '1 kilo kaju',
        qty_milli: 1000,
        unit_price_paise: 98000,
        amount_paise: 98000,
        check: false,
      },
      {
        id: fid('oline', 2),
        item_id: ITEMS.sugar.id,
        text: '2 kilo cheeni',
        qty_milli: 2000,
        unit_price_paise: 4800,
        amount_paise: 9600,
        check: false,
      },
      {
        id: fid('oline', 3),
        item_id: ITEMS.besan.id,
        text: 'besan ek packet',
        qty_milli: 1000,
        unit_price_paise: 11000,
        amount_paise: 11000,
        check: true,
      },
      {
        id: fid('oline', 4),
        item_id: ITEMS.parle.id,
        text: '5 parle',
        qty_milli: 5000,
        unit_price_paise: 1000,
        amount_paise: 5000,
        check: false,
      },
    ],
  },
  history: [],
  pick_list: [
    { item_id: ITEMS.kaju.id, name: ITEMS.kaju.name, qty_milli: 1000 },
    { item_id: ITEMS.sugar.id, name: ITEMS.sugar.name, qty_milli: 2000 },
    { item_id: ITEMS.besan.id, name: ITEMS.besan.name, qty_milli: 1000 },
    { item_id: ITEMS.parle.id, name: ITEMS.parle.name, qty_milli: 5000 },
  ],
  allowed: ['placed', 'cancelled'],
  invalidate_on: INV('order.changed'),
};

const program = (n: number, type: string, amount: number, min: number, spent: number, issued: number) => ({
  id: fid('program', n),
  type,
  status: 'active',
  funding: 'merchant',
  terms: { amount_paise: amount, min_spend_paise: min, expiry_days: 14 },
  budget_paise: 500000,
  spent_paise: spent,
  liability: {
    issued_paise: issued * amount,
    redeemed_paise: spent,
    expired_paise: 0,
    outstanding_paise: issued * amount - spent,
  },
  treated: issued,
  holdout: Math.round(issued / 9),
  issued,
  valid_until: '2026-11-15T00:00:00Z',
});

const programs = [
  program(1, 'next_txn_cashback', 2500, 50000, 37500, 42),
  program(2, 'welcome_coupon', 2000, 20000, 12000, 11),
  program(3, 'stamps', 5000, 0, 5000, 23),
];

export const offers: OffersView = {
  programs,
  liability: {
    issued_paise: programs.reduce((s, p) => s + p.liability.issued_paise, 0),
    redeemed_paise: programs.reduce((s, p) => s + p.liability.redeemed_paise, 0),
    expired_paise: 0,
    outstanding_paise: programs.reduce((s, p) => s + p.liability.outstanding_paise, 0),
  },
  invalidate_on: INV('offer.program_changed', 'offer.issued'),
};

export const offerDetail: OfferDetailView = {
  program: programs[0]!,
  issuances: [],
  invalidate_on: INV('offer.issued'),
};

export const demand: DemandView = {
  unmet: [
    { id: fid('unmet', 1), text: 'oats hai kya?', item_id: null, occurred_at: minutesAgo(3 * DAY) },
    { id: fid('unmet', 2), text: 'brown bread', item_id: null, occurred_at: minutesAgo(2 * DAY) },
    { id: fid('unmet', 3), text: 'oats ka bada packet', item_id: null, occurred_at: minutesAgo(DAY) },
  ],
  clusters: [
    { label: 'Oats', count: 7 },
    { label: 'Brown bread', count: 4 },
    { label: 'Diya / mombatti', count: 3 },
  ],
  status: 'ready',
  invalidate_on: INV('stock.demand_logged'),
};

export const storefront: StorefrontView = {
  slug: 'gupta-general-store',
  published: true,
  show_offers: true,
  items: 214,
  url: '/s/gupta-general-store',
  invalidate_on: INV('storefront.published'),
};

export const publicStorefront: PublicStorefront = {
  name: 'Gupta General Store',
  slug: 'gupta-general-store',
  hours: { start: '07:30', end: '22:00' },
  items: Object.values(ITEMS).map((i) => ({
    item_id: i.id,
    names: { en: i.name },
    unit: i.unit,
    price_paise: i.price,
    in_stock: i.id !== ITEMS.besan.id,
    category: i.cat,
  })),
  offers: [{ program_id: programs[0]!.id, terms: programs[0]!.terms, type: 'next_txn_cashback' }],
  invalidate_on: INV('storefront.published'),
};

export const hisaab: HisaabView = {
  date: '2026-10-29',
  close: { matched: 212, unmatched: 1, cash_variance_paise: -2000, cause_key: 'hisaab.cause_change' },
  today: {
    sales_paise: 418000,
    by_mode: { upi: 326000, cash: 66900 },
    expenses_paise: 15000,
    refunds_paise: 0,
    khata_given_paise: 25100,
  },
  unmatched: [
    {
      payment_id: fid('pay', 90),
      amount_paise: 34500,
      received_at: minutesAgo(35),
      khata_patron_id: PATRONS.sunita.id,
      suggestions: [{ bill_id: fid('bill', 39), total_paise: 34500, score_bp: 9100 }],
    },
  ],
  exceptions: [],
  settlements: [
    {
      id: fid('settle', 1),
      date: '2026-10-28',
      gross_paise: 912000,
      net_paise: 905600,
      deductions: [
        { kind: 'mdr', amount_paise: 0 },
        { kind: 'soundbox_rent', amount_paise: 6400 },
      ],
      explained: true,
    },
  ],
  shifts: [
    {
      id: fid('shift', 1),
      staff_id: STAFF.raju.id,
      opened_at: minutesAgo(400),
      closed_at: null,
      float_paise: 200000,
      expected_paise: 266900,
      counted_paise: null,
      variance_paise: null,
    },
  ],
  expenses: [
    {
      id: fid('exp', 1),
      category: 'chai_nashta',
      amount_paise: 15000,
      paid_from: 'cash',
      occurred_at: minutesAgo(180),
    },
  ],
  invalidate_on: INV('payment.received'),
};

export const reports: ReportsView = {
  month: '2026-10',
  profile: 'composition',
  pnl: {
    month: '2026-10',
    sales_paise: 26840000,
    returns_paise: 42000,
    cogs_paise: 22010000,
    gross_profit_paise: 4788000,
    expenses: [
      { category: 'rent', amount_paise: 1500000 },
      { category: 'electricity', amount_paise: 320000 },
      { category: 'chai_nashta', amount_paise: 90000 },
    ],
    expenses_paise: 1910000,
    reward_cost_paise: 54500,
    net_paise: 2823500,
  },
  gst: {
    month: '2026-10',
    invoices: 0,
    rates: [],
    totals: { taxable_paise: 0, cgst_paise: 0, sgst_paise: 0, total_paise: 0 },
  },
  closed_months: [{ month: '2026-09', net_paise: 2410000 }],
  scheduled: [{ id: fid('report', 1), cadence: 'weekly' }],
  invalidate_on: INV('books.month_closed'),
};

export const feedback: FeedbackView = {
  average_bp: 46000,
  count: 58,
  ratings: [
    {
      id: fid('fb', 1),
      target_kind: 'bill',
      target_id: fid('bill', 20),
      rating: 5,
      complaint_key: null,
      occurred_at: minutesAgo(300),
    },
    {
      id: fid('fb', 2),
      target_kind: 'bill',
      target_id: fid('bill', 21),
      rating: 2,
      complaint_key: 'feedback.late_delivery',
      occurred_at: minutesAgo(DAY),
    },
    {
      id: fid('fb', 3),
      target_kind: 'bill',
      target_id: fid('bill', 22),
      rating: 5,
      complaint_key: null,
      occurred_at: minutesAgo(2 * DAY),
    },
  ],
  complaints: 1,
  invalidate_on: INV('feedback.recorded'),
};

export const trust: TrustView = {
  tiers: [
    { tier: 'R0', commands: ['treasury.match_bill', 'stock.count'], confirm_key: 'trust.tier_r0' },
    { tier: 'R1', commands: ['counter.add_lines', 'ledger.send_statement'], confirm_key: 'trust.tier_r1' },
    {
      tier: 'R2',
      commands: ['counter.checkout_khata', 'catalog.change_price'],
      confirm_key: 'trust.tier_r2',
    },
    { tier: 'R3', commands: ['supply.place_po', 'ledger.send_reminder'], confirm_key: 'trust.tier_r3' },
    {
      tier: 'R4',
      commands: ['treasury.refund', 'capital.apply', 'privacy.erase_patron'],
      confirm_key: 'trust.tier_r4',
    },
  ],
  roles: [
    { role: 'owner', max_tier: 'R4', approve: ['R2', 'R3'] },
    { role: 'cashier', max_tier: 'R2', approve: [] },
    { role: 'helper', max_tier: 'R1', approve: [] },
  ],
  activity: notifications.done.map((d) => ({
    command_id: d.command_id,
    type: d.type,
    tier: d.tier,
    status: 'executed',
    actor_id: STAFF.ramesh.id,
    occurred_at: d.occurred_at,
  })),
  audit: { ok: true, rows: 1284 },
  undo: [{ command_id: fid('cmd', 1), type: 'ledger.send_statement', until: minutesAhead(0.4) }],
  data_sharing: { peer_benchmarks: true },
  data_requests: [],
  invalidate_on: INV('command.executed'),
};

export const health: HealthView = {
  device: { battery_pct: 82, network: 'wifi', firmware: '4.2.1', last_seen_at: NOW, speaker: 'ok' },
  offline_queue: { size: 0, last_sync_at: minutesAgo(1) },
  providers: [
    { name: 'sarvam', configured: true, mode: 'live' },
    { name: 'mistral', configured: true, mode: 'live' },
    { name: 'groq', configured: true, mode: 'fallback' },
  ],
  ai_spend_today_paise: 1840,
  backup: { last_snapshot_at: minutesAgo(380) },
  invalidate_on: INV('device.health_reported'),
};

export const capital: CapitalView = {
  profile: { monthly_sales_paise: 26840000 },
  need: { purpose_key: 'capital.purpose_diwali_stock', shortfall_paise: 6000000, shortfall_on: '2026-11-03' },
  affordability: { max_edi_paise: 150000 },
  offers: [
    {
      id: fid('offer', 1),
      lender: 'Paytm Lending Partner (simulated)',
      amount_paise: 7500000,
      tenor_days: 90,
      apr_bp: 2100,
      edi_paise: 89000,
      processing_fee_paise: 75000,
      total_repayment_paise: 8010000,
      kfs_url: '/console/capital/kfs',
      cooling_off_days: 3,
      expires_at: '2026-11-05T00:00:00Z',
      affordable: true,
    },
  ],
  recommended_offer_id: fid('offer', 1),
  console_pointer: { route: '/console/capital', message_key: 'capital.console_only' },
  invalidate_on: INV('capital.offer_received'),
};

export const kot: KotView = {
  tickets: [
    {
      id: fid('ticket', 1),
      bill_id: fid('bill', 60),
      token: 7,
      status: 'new',
      age_seconds: 40,
      items: [{ name: 'Masala chai', qty_milli: 2000, modifiers: ['Less sugar'] }],
    },
    {
      id: fid('ticket', 2),
      bill_id: fid('bill', 61),
      token: 6,
      status: 'preparing',
      age_seconds: 260,
      items: [
        { name: 'Veg sandwich', qty_milli: 1000, modifiers: ['Grilled'] },
        { name: 'Cold coffee', qty_milli: 1000, modifiers: [] },
      ],
    },
    {
      id: fid('ticket', 3),
      bill_id: fid('bill', 62),
      token: 5,
      status: 'ready',
      age_seconds: 540,
      items: [{ name: 'Poha', qty_milli: 1000, modifiers: [] }],
    },
    {
      id: fid('ticket', 4),
      bill_id: fid('bill', 63),
      token: 4,
      status: 'served',
      age_seconds: 900,
      items: [{ name: 'Masala chai', qty_milli: 1000, modifiers: [] }],
    },
  ],
  invalidate_on: INV('bill.ticket_changed'),
};

export const appointments: AppointmentsView = {
  date: '2026-10-29',
  staff: [
    {
      id: fid('staff', 11),
      name: 'Anita',
      skills: ['haircut', 'facial'],
      appointments: [
        {
          id: fid('appt', 1),
          service_item_id: fid('item', 51),
          staff_id: fid('staff', 11),
          patron_id: PATRONS.priya.id,
          start_at: '2026-10-29T05:30:00Z',
          end_at: '2026-10-29T06:15:00Z',
          status: 'done',
          source: 'whatsapp',
        },
        {
          id: fid('appt', 2),
          service_item_id: fid('item', 52),
          staff_id: fid('staff', 11),
          patron_id: PATRONS.sunita.id,
          start_at: '2026-10-29T09:30:00Z',
          end_at: '2026-10-29T10:30:00Z',
          status: 'booked',
          source: 'storefront',
        },
      ],
    },
    {
      id: fid('staff', 12),
      name: 'Imran',
      skills: ['haircut', 'shave'],
      appointments: [
        {
          id: fid('appt', 3),
          service_item_id: fid('item', 53),
          staff_id: fid('staff', 12),
          patron_id: PATRONS.rohit.id,
          start_at: '2026-10-29T08:30:00Z',
          end_at: '2026-10-29T09:00:00Z',
          status: 'checked_in',
          source: 'walk_in',
        },
      ],
    },
  ],
  walk_ins: [
    {
      id: fid('appt', 4),
      service_item_id: fid('item', 53),
      staff_id: null,
      patron_id: null,
      start_at: null,
      end_at: null,
      status: 'waiting',
      source: 'walk_in',
    },
  ],
  no_shows: 1,
  invalidate_on: INV('order.appointment_changed'),
};

export const rx: RxView = {
  rx_sales: [
    {
      bill_id: fid('bill', 70),
      item_id: fid('item', 71),
      name: 'Azithromycin 500',
      staff_id: STAFF.raju.id,
      occurred_at: minutesAgo(70),
    },
  ],
  refills_due: [
    {
      patron_id: PATRONS.sharma.id,
      item_id: fid('item', 72),
      due_on: '2026-10-31',
      patron_name: PATRONS.sharma.name,
      item_name: 'Metformin 500',
    },
  ],
  recalls: [],
  invalidate_on: INV('bill.paid', 'batch.recalled'),
};

export const verdict: VerdictView = {
  check_id: fid('sentinel', 1),
  verdict: 'not_received',
  headline_key: 'sentinel.not_received_yet',
  evidence: [
    { kind: 'amount', claimed: '50000', ledger: null, state: 'missing' },
    { kind: 'utr', claimed: '629104889999', ledger: null, state: 'missing' },
    { kind: 'payee', claimed: 'guptastore@paytm', ledger: 'guptastore@paytm', state: 'match' },
    { kind: 'time', claimed: '2026-10-29T08:31:00Z', ledger: null, state: 'missing' },
  ],
  signals: [],
  footnote_key: 'sentinel.ledger_only',
  invalidate_on: INV('sentinel.verdict', 'payment.received'),
};

export const settings: SettingsView = {
  name: 'Gupta General Store',
  pack: 'kirana',
  screen_lang: 'hi-Latn',
  speech_lang: 'hi-IN',
  customer_lang: 'hi',
  tax_profile: 'composition',
  marketing_consent_default: false,
  receipts_consent_default: false,
};

export const staffView: StaffView = {
  staff: Object.values(STAFF).map((s) => ({ id: s.id, name: s.name, role: s.role })),
  invalidate_on: INV('staff.added'),
};

export const shift: ShiftView = {
  current: {
    id: fid('shift', 1),
    staff_id: STAFF.raju.id,
    opened_at: minutesAgo(400),
    closed_at: null,
    float_paise: 200000,
    expected_paise: 266900,
    counted_paise: null,
    variance_paise: null,
  },
  invalidate_on: INV('staff.shift_opened', 'staff.shift_closed'),
};

export const onboarding: OnboardingView = {
  steps: ['language', 'pack', 'details', 'catalog', 'people'],
  completed: ['language', 'pack'],
  next_step: 'details',
  invalidate_on: INV('onboarding.updated'),
};

export const IDS = { BILL_ID, PAID_BILL_ID, PO_ID, CLAIM_ID, GATES };
