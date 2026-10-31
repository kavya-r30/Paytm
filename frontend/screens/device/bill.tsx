'use client';

// J2 · Bill: SCR-BILL (+ SCR-CUSTPICK sheet, café SCR-MODS), SCR-PAY, SCR-PAID, SCR-LEARN, SCR-VERDICT,
// SCR-RETURN, SCR-PARK, SCR-ORDERS / SCR-ORDER.
import {
  Camera,
  Check,
  CircleAlert,
  Printer,
  QrCode,
  ScanLine,
  Search,
  Smartphone,
  Wallet,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { ArthNote, Orb } from '@/components/arth/orb';
import { Empty, Screen, Sheet, useAction, useDeviceNav } from '@/components/shell/device';
import {
  Avatar,
  Button,
  Card,
  Chip,
  Money,
  Pill,
  SectionTitle,
  TierChip,
  Toggle,
  cx,
} from '@/components/ui/kit';
import { apiGet } from '@/lib/api/client';
import { useCommand } from '@/lib/api/commands';
import { useDataMode, useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import type { BillView, CatalogSearchView } from '@/lib/contracts';
import { IDS, ITEMS, PATRONS } from '@/lib/fixtures/gupta';
import { qty } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, type ScreenProps } from './common';

type GridItem = { id: string; name: string; price: number; unit: string; cat: string };

/**
 * Item grid: the view's quick_items (most-sold first) filtered by category chip; typing searches the catalog
 * in live mode and filters the quick items in fixture mode.
 */
function useGrid(view: BillView | undefined, query: string, cat: string): GridItem[] {
  const mode = useDataMode();
  const { locale } = useI18n();
  const q = useQuery({
    queryKey: ['catalog', query, mode],
    enabled: mode === 'live' && query.length > 0,
    queryFn: async () =>
      (await apiGet(`/v1/catalog/search?q=${encodeURIComponent(query)}`)) as CatalogSearchView,
  });
  if (mode === 'live' && query) {
    return (q.data?.items ?? []).map((i) => ({
      id: i.id,
      name: i.names[locale] ?? i.names.en ?? Object.values(i.names)[0] ?? i.sku,
      price: i.price_paise,
      unit: i.unit ?? 'pcs',
      cat: i.category ?? '',
    }));
  }
  const all = (view?.quick_items ?? []).map((i) => ({
    id: i.item_id,
    name: i.name,
    price: i.price_paise,
    unit: i.unit,
    cat: i.category,
  }));
  if (query) return all.filter((i) => i.name.toLowerCase().includes(query.toLowerCase()));
  const first = view?.categories[0]?.key;
  return cat === first ? all.slice(0, 12) : all.filter((i) => i.cat === cat);
}

const ITEM_TINT = ['bg-amber-tint', 'bg-sky', 'bg-green-tint', 'bg-red-tint'];

function ItemTile({ item, onAdd }: { item: GridItem; onAdd: () => void }) {
  const { money } = useI18n();
  const tint = ITEM_TINT[item.name.length % ITEM_TINT.length];
  return (
    <button
      type="button"
      onClick={onAdd}
      className="flex h-[112px] flex-col justify-between rounded-card bg-white p-4 text-left shadow-1 transition hover:shadow-2 active:scale-[0.98]"
    >
      <span
        className={cx(
          'flex h-11 w-11 items-center justify-center rounded-ground text-body font-extrabold text-midnight',
          tint,
        )}
      >
        {item.name.slice(0, 1)}
      </span>
      <span>
        <span className="line-clamp-2 text-body font-bold leading-tight text-ink">{item.name}</span>
        <span className="num text-body text-ink-3">
          {money(item.price)}
          {item.unit === 'kg' ? '/kg' : ''}
        </span>
      </span>
    </button>
  );
}

function PatronChip({ patron, onChange }: { patron: BillView['bill']['patron']; onChange: () => void }) {
  const { t, money } = useI18n();
  if (!patron) {
    return (
      <button
        type="button"
        onClick={onChange}
        className="flex w-full items-center gap-3 rounded-ground border-2 border-dashed border-line p-4 text-left"
      >
        <Avatar name="+" tone="sky" />
        <span className="text-body font-bold text-cyan-text">{t('bill.add_customer')}</span>
      </button>
    );
  }
  return (
    <div className="flex items-center gap-3 rounded-ground bg-sky p-3">
      <Avatar name={patron.display_name} size={48} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-arth font-bold text-ink">{patron.display_name}</p>
        <p className="truncate text-meta text-ink-3">
          {t(patron.khata_balance_paise ? 'bill.patron_status_due' : 'bill.patron_status', {
            stamps: patron.reward_stamps,
            total: 10,
            due: patron.khata_balance_paise ? money(patron.khata_balance_paise) : '',
          })}{' '}
          · {t(`lang.${patron.lang}`)}
        </p>
      </div>
      <Button variant="text" onClick={onChange}>
        {t('common.change')}
      </Button>
    </div>
  );
}

/** SCR-CUSTPICK overlay: search, recent patrons, walk-in, new patron with consent toggles. */
function CustomerPicker({
  open,
  onClose,
  onPick,
}: {
  open: boolean;
  onClose: () => void;
  onPick: (id: string | null) => void;
}) {
  const { t } = useI18n();
  const [q, setQ] = useState('');
  const state = useView(views.customers(q), { enabled: open });
  const [consent, setConsent] = useState({ receipts: true, marketing: false });
  const [lang, setLang] = useState('hi');
  return (
    <Sheet open={open} onClose={onClose}>
      <div className="grid grid-cols-2">
        <div className="border-r border-line p-6">
          <h2 className="text-title">{t('custpick.title')}</h2>
          <label className="mt-4 flex h-12 items-center gap-2 rounded-ground bg-ground px-4">
            <Search size={18} className="text-ink-3" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={t('custpick.search')}
              className="flex-1 bg-transparent text-body outline-none"
            />
          </label>
          <ul className="no-scrollbar mt-3 max-h-[360px] divide-y divide-line overflow-y-auto">
            {(q.trim()
              ? (state.data?.customers ?? []).map((c) => ({
                  ...c,
                  phone_masked: null,
                  khata_balance_paise: null,
                  reward_stamps: 0,
                }))
              : (state.data?.recent ?? [])
            ).map((c) => (
              <li key={c.patron_id}>
                <button
                  type="button"
                  onClick={() => onPick(c.patron_id)}
                  className="flex w-full items-center gap-3 py-3 text-left"
                >
                  <Avatar name={c.display_name} size={40} />
                  <span className="flex-1">
                    <span className="block text-body font-bold">{c.display_name}</span>
                    <span className="block text-meta text-ink-3">{c.phone_masked ?? ''}</span>
                  </span>
                  {c.khata_balance_paise ? (
                    <Pill tone="red">
                      <Money paise={c.khata_balance_paise} />
                    </Pill>
                  ) : c.reward_stamps > 0 ? (
                    <Pill tone="green">{t('custpick.stamps', { n: c.reward_stamps })}</Pill>
                  ) : (
                    <Pill tone="sky">{t('custpick.regular')}</Pill>
                  )}
                </button>
              </li>
            ))}
          </ul>
          <Button variant="ghost" className="mt-3 w-full" onClick={() => onPick(null)}>
            {t('custpick.walk_in')}
          </Button>
        </div>
        <div className="flex flex-col gap-4 bg-ground/60 p-6 pt-16">
          <ArthNote>{t('custpick.first_time')}</ArthNote>
          <input
            placeholder={t('custpick.name')}
            className="h-12 rounded-ground border border-line bg-white px-4 text-body"
          />
          <input
            placeholder={t('custpick.phone')}
            className="h-12 rounded-ground border border-line bg-white px-4 text-body"
          />
          <div>
            <p className="mb-2 text-meta font-semibold text-ink-3">{t('custpick.msg_lang')}</p>
            <div className="flex gap-2">
              {['hi', 'hi-Latn', 'en'].map((l) => (
                <Chip key={l} active={lang === l} onClick={() => setLang(l)}>
                  {t(`lang.${l}`)}
                </Chip>
              ))}
            </div>
          </div>
          <div className="space-y-3 rounded-ground bg-white p-4">
            {(['receipts', 'marketing'] as const).map((k) => (
              <div key={k} className="flex items-center justify-between gap-3">
                <span className="text-body">{t(`custpick.consent_${k}`)}</span>
                <Toggle
                  on={consent[k]}
                  onChange={(v) => setConsent((c) => ({ ...c, [k]: v }))}
                  label={t(`custpick.consent_${k}`)}
                />
              </div>
            ))}
            <p className="text-meta text-ink-3">{t('custpick.cap_note')}</p>
          </div>
          <Button onClick={() => onPick(PATRONS.rohit.id)}>{t('custpick.add_and_attach')}</Button>
        </div>
      </div>
    </Sheet>
  );
}

function BillPanel({ view }: { view: BillView }) {
  const { t, money } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const [picker, setPicker] = useState(false);
  const [mode, setMode] = useState<'upi' | 'cash' | 'khata'>('upi');
  const bill = view.bill;
  // GRW-4: the counter hint is owner-only and absent for holdout bills; never shown on the customer display.
  const hint = view.hint && !bill.lines.some((l) => l.item_id === view.hint!.item_id) ? view.hint : null;

  const pay = useCallback(
    async (m: typeof mode) => {
      if (m === 'upi') {
        await run('counter.request_upi', { bill_id: bill.id });
        nav(`bill/${bill.id}/pay`);
      } else if (m === 'cash') {
        const r = await run('counter.checkout', {
          bill_id: bill.id,
          payments: [{ mode: 'cash', amount_paise: bill.due_paise, tendered_paise: bill.due_paise }],
        });
        if (r.kind === 'done' || r.kind === 'offline') nav(`bill/${bill.id}/paid`);
      } else {
        nav(`khata/${bill.patron_id ?? ''}`);
      }
    },
    [bill, nav, run],
  );
  useAction(
    useCallback(
      (a: string) => {
        if (a === 'show_qr') void pay('upi');
        if (a === 'pay_cash') void pay('cash');
        if (a === 'pay_khata') void pay('khata');
      },
      [pay],
    ),
  );

  return (
    <Card className="flex h-full flex-col overflow-hidden">
      <div className="p-4">
        <PatronChip patron={bill.patron} onChange={() => setPicker(true)} />
      </div>
      <ul className="no-scrollbar flex-1 overflow-y-auto">
        {bill.lines.length === 0 && <Empty title={t('bill.empty')} body={t('bill.empty_body')} />}
        {bill.lines.map((l, i) => (
          <li
            key={l.id}
            className={cx(
              'flex items-center gap-3 px-5 py-3',
              i === bill.lines.length - 1 && l.added_via === 'voice' && 'bg-sky',
            )}
          >
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-ground bg-amber-tint font-extrabold text-midnight">
              {l.name.slice(0, 1)}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-body font-bold">{l.name}</span>
              <span className="text-meta text-ink-3">
                {qty(l.qty_milli)} ·{' '}
                <span className={l.added_via === 'voice' ? 'font-semibold text-cyan-text' : ''}>
                  {t(`bill.via_${l.added_via}`)}
                </span>
              </span>
            </span>
            <Money paise={l.amount_paise} className="text-arth font-bold" />
          </li>
        ))}
      </ul>
      {hint && (
        <div className="mx-4 mb-2 flex items-center gap-3 rounded-ground border-2 border-paytm-blue p-3">
          <p className="flex-1 text-body leading-snug">
            <span className="font-bold text-midnight">{t('arth.name')}: </span>
            {t(hint.reason_key, { name: bill.patron?.display_name ?? '', item: hint.name })}
          </p>
          <Button
            variant="tint"
            size="sm"
            onClick={async () => {
              await run(
                'counter.add_lines',
                { bill_id: bill.id, lines: [{ item_id: hint.item_id, qty_milli: 1000, added_via: 'hint' }] },
                { undo: { type: 'counter.undo', payload: { bill_id: bill.id } } },
              );
              void run('hints.accept', { hint_id: hint.hint_id });
            }}
          >
            + {money(hint.price_paise)}
          </Button>
        </div>
      )}
      <div className="border-t border-line p-4">
        <div className="flex items-end justify-between">
          <span className="text-body text-ink-3">{t('bill.items', { n: bill.lines.length })}</span>
          <Money paise={bill.total_paise} className="text-4xl font-extrabold leading-none" />
        </div>
        <div className="mt-3 flex gap-2">
          {(['upi', 'cash', 'khata'] as const).map((m) => (
            <Chip key={m} tone={m === 'khata' ? 'red' : 'sky'} active={mode === m} onClick={() => setMode(m)}>
              {t(`pay.${m}`)}
            </Chip>
          ))}
        </div>
        <Button
          size="lg"
          className="mt-3 w-full"
          icon={<QrCode size={24} />}
          disabled={!bill.lines.length}
          onClick={() => void pay(mode)}
        >
          {mode === 'upi'
            ? t('bill.show_qr', { total: money(bill.total_paise) })
            : mode === 'cash'
              ? t('bill.take_cash', { total: money(bill.total_paise) })
              : t('bill.to_khata', { total: money(bill.total_paise) })}
        </Button>
      </div>
      <CustomerPicker
        open={picker}
        onClose={() => setPicker(false)}
        onPick={(id) => {
          setPicker(false);
          if (id) void run('counter.attach_patron', { bill_id: bill.id, patron_id: id });
        }}
      />
    </Card>
  );
}

function NewBill() {
  const run = useCommand();
  const nav = useDeviceNav();
  const mode = useDataMode();
  useEffect(() => {
    if (mode === 'fixture') {
      nav(`bill/${IDS.BILL_ID}`);
      return;
    }
    void run('counter.open_bill', {}).then((r) => {
      const id = r.kind === 'done' ? (r.result.data?.bill_id as string | undefined) : undefined;
      if (id) nav(`bill/${id}`);
    });
  }, [mode, nav, run]);
  return <Orb state="thinking" size={96} className="m-auto" />;
}

export function BillScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const [query, setQuery] = useState('');
  const isNew = !param || param === 'new';
  const state = useView(views.bill(param ?? 'new'), { enabled: !isNew });
  const [picked, setCat] = useState<string | null>(null);
  const cat = picked ?? state.data?.categories[0]?.key ?? '';
  const grid = useGrid(state.data, query, cat);
  if (isNew) return <NewBill />;
  const billNo = param!.slice(-4);
  return (
    <Screen
      title={t('bill.title', { n: billNo })}
      sub={t('bill.sub')}
      right={
        <div className="flex items-center gap-3">
          {(state.data?.parked_count ?? 0) > 0 && (
            <Button variant="tint" size="sm" onClick={() => nav('park')}>
              {t('bill.parked', { n: state.data!.parked_count })}
            </Button>
          )}
          <Button
            variant="text"
            onClick={() => void run('counter.park', { bill_id: param }).then(() => nav('park'))}
          >
            {t('bill.park')}
          </Button>
        </div>
      }
      chips={[
        { label: t('bill.chip_qr'), text: 'QR dikhao' },
        { label: t('bill.chip_remove'), text: 'hatao' },
      ]}
    >
      <ViewGate state={state}>
        {(view) => (
          <div className="grid h-full grid-cols-[minmax(0,1fr)_340px] gap-4">
            <div className="flex min-h-0 flex-col gap-4">
              <div className="flex gap-3">
                <label className="flex h-14 min-w-0 flex-1 items-center gap-3 rounded-card bg-white px-5 shadow-1">
                  <Search size={20} className="text-ink-3" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={t('bill.search')}
                    className="w-full min-w-0 flex-1 bg-transparent text-body outline-none"
                  />
                </label>
                <Button
                  variant="dark"
                  icon={<ScanLine size={20} />}
                  onClick={() => nav('learn')}
                  className="h-14 shrink-0"
                >
                  {t('bill.scan')}
                </Button>
              </div>
              <div className="no-scrollbar flex gap-2 overflow-x-auto">
                {view.categories.map((c) => (
                  <Chip
                    key={c.key}
                    active={cat === c.key}
                    tone={c.key === 'diwali' ? 'amber' : 'plain'}
                    onClick={() => setCat(c.key)}
                  >
                    {t(`bill.cat_${c.key}`) === `bill.cat_${c.key}` ? c.label : t(`bill.cat_${c.key}`)}
                  </Chip>
                ))}
              </div>
              <div className="no-scrollbar grid min-h-0 grid-cols-3 content-start gap-3 overflow-y-auto pb-2">
                {grid.map((item) => (
                  <ItemTile
                    key={item.id}
                    item={item}
                    onAdd={() =>
                      void run(
                        'counter.add_lines',
                        {
                          bill_id: view.bill.id,
                          lines: [{ item_id: item.id, qty_milli: 1000, added_via: 'tapped' }],
                        },
                        {
                          label: 'counter.add_lines',
                          undo: { type: 'counter.undo', payload: { bill_id: view.bill.id } },
                        },
                      )
                    }
                  />
                ))}
              </div>
            </div>
            <BillPanel view={view} />
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

function useCountdown(until: string | null | undefined) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);
  if (!until) return null;
  return Math.max(0, Math.round((Date.parse(until) - now) / 1000));
}

/** A QR-like grid generated from the order ref: the simulator's real QR image arrives with the Rails page. */
export function FakeQr({ seed, size = 220 }: { seed: string; size?: number }) {
  const cells = 25;
  const bits = useMemo(() => {
    let h = 2166136261;
    return Array.from({ length: cells * cells }, (_, i) => {
      h = Math.imul(h ^ (seed.charCodeAt(i % seed.length) + i), 16777619);
      return (h >>> 7) & 1;
    });
  }, [seed]);
  const finder = (x: number, y: number) =>
    (x < 7 && y < 7) || (x >= cells - 7 && y < 7) || (x < 7 && y >= cells - 7);
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${cells} ${cells}`}
      shapeRendering="crispEdges"
      aria-label="UPI QR"
    >
      <rect width={cells} height={cells} fill="white" />
      {bits.map((b, i) => {
        const x = i % cells;
        const y = Math.floor(i / cells);
        if (finder(x, y)) return null;
        return b ? <rect key={i} x={x} y={y} width={1} height={1} fill="var(--color-ink)" /> : null;
      })}
      {[
        [0, 0],
        [cells - 7, 0],
        [0, cells - 7],
      ].map(([x, y]) => (
        <g key={`${x}-${y}`}>
          <rect x={x} y={y} width={7} height={7} fill="var(--color-ink)" />
          <rect x={x! + 1} y={y! + 1} width={5} height={5} fill="white" />
          <rect x={x! + 2} y={y! + 2} width={3} height={3} fill="var(--color-ink)" />
        </g>
      ))}
    </svg>
  );
}

export function PayScreen({ param }: ScreenProps) {
  const { t, money } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const id = param ?? IDS.BILL_ID;
  const state = useView(views.billPay(id));
  const left = useCountdown(state.data?.bill.upi?.expires_at);
  const status = state.data?.bill.upi?.status ?? 'waiting';
  useEffect(() => {
    if (status === 'paid' || state.data?.bill.status === 'closed') nav(`bill/${id}/paid`);
  }, [status, state.data, id, nav]);
  return (
    <Screen
      title={t('pay.title')}
      sub={t('pay.sub')}
      chips={[{ label: t('pay.chip_cash'), text: 'Cash mein lo' }]}
    >
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-2 gap-5">
            <Card className="flex flex-col items-center gap-4 p-8">
              <Money paise={v.bill.due_paise} className="text-amount font-extrabold" />
              <div className="rounded-card border-4 border-line p-3">
                <FakeQr seed={v.bill.upi?.order_ref ?? v.bill.id} size={240} />
              </div>
              <p className="text-body font-semibold text-ink-2">{v.payee_vpa}</p>
              <p className="flex items-center gap-2 text-meta text-ink-3">
                <Smartphone size={16} /> {t('pay.on_display')}
              </p>
              {left !== null && (
                <Pill tone={left < 60 ? 'amber' : 'grey'}>
                  {t('pay.valid_for', {
                    s: `${Math.floor(left / 60)}:${String(left % 60).padStart(2, '0')}`,
                  })}
                </Pill>
              )}
            </Card>
            <div className="flex flex-col gap-4">
              <Card className="flex items-center gap-5 p-6">
                <Orb state={status === 'failed' ? 'alert' : 'thinking'} size={72} />
                <div>
                  <p className="text-title">{t(`pay.status_${status}`)}</p>
                  <p className="text-body text-ink-3">{t('pay.waiting_sub')}</p>
                </div>
              </Card>
              {v.exception && <ArthNote>{t('pay.exception')}</ArthNote>}
              <Button
                variant="ghost"
                size="lg"
                icon={<Wallet size={22} />}
                onClick={() =>
                  void run('counter.checkout', {
                    bill_id: v.bill.id,
                    payments: [
                      { mode: 'cash', amount_paise: v.bill.due_paise, tendered_paise: v.bill.due_paise },
                    ],
                  }).then(() => nav(`bill/${v.bill.id}/paid`))
                }
              >
                {t('pay.take_cash')}
              </Button>
              <Button
                variant="ghost"
                size="lg"
                className="text-red"
                onClick={() => nav(`khata/${v.bill.patron_id ?? ''}`)}
              >
                {t('pay.to_khata')} · <TierChip tier="R2" />
              </Button>
              <Button variant="text" onClick={() => nav(`bill/${v.bill.id}`)}>
                {t('pay.edit_bill')}
              </Button>
              {status === 'expired' && (
                <Button onClick={() => void run('counter.request_upi', { bill_id: v.bill.id })}>
                  {t('pay.regenerate')}
                </Button>
              )}
              <p className="num text-center text-meta text-ink-3">{money(v.bill.total_paise)}</p>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function PaidScreen({ param }: ScreenProps) {
  const { t, time } = useI18n();
  const nav = useDeviceNav();
  const state = useView(views.billPaid(param ?? IDS.PAID_BILL_ID));
  return (
    <Screen
      title={t('paid.title')}
      sub={t('paid.sub')}
      chips={[{ label: t('paid.chip_new'), text: 'Naya bill' }]}
    >
      <ViewGate state={state}>
        {(v) => {
          const p = v.bill.payments[0];
          const patron = v.bill.patron_id;
          return (
            <div className="grid grid-cols-2 gap-5">
              <div className="flex flex-col gap-4">
                <div className="flex flex-col items-center gap-3 rounded-card bg-green-tint p-8">
                  <Orb state="done" size={88} />
                  <p className="text-arth font-bold text-green">
                    {t('paid.received', {
                      mode: t(`pay.${p?.mode ?? 'upi'}`),
                      time: time(v.bill.closed_at ?? v.bill.opened_at),
                    })}
                  </p>
                  <Money paise={v.bill.total_paise} className="text-amount font-extrabold text-green" />
                  {patron && <PatronName id={patron} />}
                  <div className="flex gap-1.5" aria-label={t('paid.reward')}>
                    {Array.from({ length: 10 }, (_, i) => (
                      <span
                        key={i}
                        className={cx('h-3 w-3 rounded-chip', i < 4 ? 'bg-green-fill' : 'bg-white')}
                      />
                    ))}
                  </div>
                  {v.utr_tail && (
                    <p className="num text-meta text-ink-3">{t('paid.utr', { tail: v.utr_tail })}</p>
                  )}
                </div>
                {v.offers.map((o) => (
                  <Card key={o.issuance_id} className="flex items-center gap-3 p-4">
                    <Pill tone="green">{t('paid.offer_issued')}</Pill>
                    <span className="text-body">
                      {t(`offer_kind.${o.kind}`)} · <Money paise={o.amount_paise} />
                    </span>
                  </Card>
                ))}
                <div className="flex gap-3">
                  <Button size="lg" className="flex-1" onClick={() => nav('bill/new')}>
                    {t('paid.new_bill')}
                  </Button>
                  <Button variant="ghost" size="lg" icon={<Printer size={20} />}>
                    {t('paid.print')}
                  </Button>
                </div>
              </div>
              <Card className="flex flex-col p-6">
                <SectionTitle action={<Button variant="text">{t('common.change')}</Button>}>
                  {t('paid.receipt')}
                </SectionTitle>
                <div className="flex-1 rounded-ground bg-ground p-4 text-body">
                  {v.bill.lines.map((l) => (
                    <div key={l.id} className="flex justify-between py-1">
                      <span>
                        {l.name} × {qty(l.qty_milli)}
                      </span>
                      <Money paise={l.amount_paise} />
                    </div>
                  ))}
                  <div className="mt-2 flex justify-between border-t border-line pt-2 font-bold">
                    <span>{t('paid.total')}</span>
                    <Money paise={v.bill.total_paise} />
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  {v.receipt.status === 'queued' ? (
                    <Pill tone="green">
                      <Check size={14} /> {t('paid.receipt_sent')}
                    </Pill>
                  ) : (
                    <Pill tone="amber">{t(`paid.receipt_${v.receipt.status}`)}</Pill>
                  )}
                  <Button variant="text">{t('paid.pdf')}</Button>
                  <Button variant="text">{t('paid.sms')}</Button>
                </div>
              </Card>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}

function PatronName({ id }: { id: string }) {
  return <p className="text-body font-semibold text-ink">{useName(id)}</p>;
}

export function LearnScreen(_: ScreenProps) {
  const { t, money } = useI18n();
  const run = useCommand();
  const [price, setPrice] = useState(5500);
  return (
    <Screen
      title={t('learn.title')}
      sub={t('learn.sub')}
      chips={[{ label: t('learn.chip_price'), text: 'Haan, ₹55 rakho' }]}
    >
      <div className="grid grid-cols-2 gap-5">
        <Card className="flex aspect-[4/3] flex-col items-center justify-center gap-3 bg-ink text-white">
          <Camera size={48} />
          <p className="text-body">{t('learn.camera')}</p>
        </Card>
        <Card className="flex flex-col gap-4 p-6">
          <SectionTitle action={<Pill tone="green">{t('learn.confidence', { pct: 92 })}</Pill>}>
            {t('learn.extracted')}
          </SectionTitle>
          {[
            ['learn.name', 'Haldiram Bhujia 200 g'],
            ['learn.net_qty', '200 g'],
            ['learn.mrp', money(5500)],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between border-b border-line pb-2">
              <span className="text-body text-ink-3">{t(k!)}</span>
              <span className="text-body font-bold">{v}</span>
            </div>
          ))}
          <label className="flex items-center justify-between">
            <span className="text-body text-ink-3">{t('learn.price')}</span>
            <input
              type="number"
              value={price / 100}
              onChange={(e) => setPrice(Math.round(Number(e.target.value) * 100))}
              className="num h-11 w-32 rounded-ground border border-line px-3 text-right text-arth font-bold"
            />
          </label>
          <div className="flex items-center gap-2">
            <TierChip tier="R2" />
            <span className="text-meta text-ink-3">{t('learn.readback', { price: money(price) })}</span>
          </div>
          <Button
            size="lg"
            onClick={() =>
              void run('catalog.add_item', {
                names: { en: 'Haldiram Bhujia 200 g' },
                unit: 'pcs',
                price_paise: price,
                mrp_paise: 5500,
              })
            }
          >
            {t('learn.save')}
          </Button>
        </Card>
      </div>
    </Screen>
  );
}

export function VerdictScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.verdict(param ?? 'latest'));
  return (
    <Screen title={t('verdict.title')} sub={t('verdict.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[280px_1fr] gap-5">
            <Card className="flex aspect-[9/16] items-center justify-center bg-ground p-4 text-center text-meta text-ink-3">
              {t('verdict.forwarded')}
            </Card>
            <div className="flex flex-col gap-4">
              <div
                className={cx(
                  'flex items-center gap-4 rounded-card p-6',
                  v.verdict === 'received'
                    ? 'bg-green-tint'
                    : v.verdict === 'not_received'
                      ? 'bg-red-tint'
                      : 'bg-amber-tint',
                )}
              >
                <Orb state={v.verdict === 'received' ? 'done' : 'alert'} size={64} />
                <p className="text-title">{t(v.headline_key)}</p>
              </div>
              <Card className="p-5">
                <div className="grid grid-cols-[1fr_1fr_1fr_auto] gap-3 border-b border-line pb-2 text-meta font-semibold text-ink-3">
                  <span />
                  <span>{t('verdict.screenshot_says')}</span>
                  <span>{t('verdict.ledger_says')}</span>
                  <span />
                </div>
                {v.evidence.map((e) => (
                  <div
                    key={e.kind}
                    className="grid grid-cols-[1fr_1fr_1fr_auto] items-center gap-3 border-b border-line py-3 text-body"
                  >
                    <span className="font-semibold">{t(`verdict.kind_${e.kind}`)}</span>
                    <span className="num truncate">{e.claimed ?? '—'}</span>
                    <span className="num truncate">{e.ledger ?? t('verdict.not_found')}</span>
                    <Pill tone={e.state === 'match' ? 'green' : e.state === 'mismatch' ? 'red' : 'amber'}>
                      {t(`verdict.state_${e.state}`)}
                    </Pill>
                  </div>
                ))}
              </Card>
              <p className="text-meta text-ink-3">{t(v.footnote_key)}</p>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function ReturnScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.billPaid(param ?? IDS.PAID_BILL_ID));
  const [refund, setRefund] = useState<'cash' | 'credit' | 'upi'>('cash');
  return (
    <Screen title={t('return.title')} sub={t('return.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_360px] gap-5">
            <Card className="p-6">
              {v.bill.lines.map((l) => (
                <div key={l.id} className="flex items-center gap-3 border-b border-line py-3">
                  <span className="flex-1 text-body font-semibold">{l.name}</span>
                  <span className="num text-meta text-ink-3">× {qty(l.qty_milli)}</span>
                  <input
                    type="number"
                    defaultValue={0}
                    min={0}
                    className="num h-10 w-20 rounded-ground border border-line px-2 text-right"
                    aria-label={t('return.qty')}
                  />
                </div>
              ))}
            </Card>
            <Card className="flex flex-col gap-4 p-6">
              <SectionTitle>{t('return.refund_mode')}</SectionTitle>
              {(['cash', 'credit', 'upi'] as const).map((m) => (
                <Chip key={m} active={refund === m} onClick={() => setRefund(m)} className="justify-between">
                  {t(`return.mode_${m}`)} <TierChip tier={m === 'upi' ? 'R4' : 'R2'} />
                </Chip>
              ))}
              {refund === 'upi' ? (
                <ArthNote>{t('return.console_pointer')}</ArthNote>
              ) : (
                <Button
                  onClick={() =>
                    void run('counter.return', { bill_id: v.bill.id, lines: [], refund_mode: refund }).then(
                      () => nav('home'),
                    )
                  }
                >
                  {t('return.confirm')}
                </Button>
              )}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function ParkScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.park());
  return (
    <Screen title={t('park.title')} sub={t('park.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-2 gap-4">
            {v.bills.length === 0 && <Empty title={t('park.none')} />}
            {v.bills.map((b) => (
              <Card key={b.id} className="flex items-center gap-4 p-5">
                <span className="text-body font-bold">{b.patron_name ?? t('custpick.walk_in')}</span>
                <span className="num text-meta text-ink-3">
                  {t('park.lines', { n: b.lines })} · {time(b.opened_at)}
                </span>
                <Money paise={b.total_paise} className="ml-auto text-arth font-bold" />
                <Button
                  variant="dark"
                  size="sm"
                  onClick={() =>
                    void run('counter.resume', { bill_id: b.id }).then(() => nav(`bill/${b.id}`))
                  }
                >
                  {t('park.resume')}
                </Button>
              </Card>
            ))}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

function PatronOrWalkIn({ id }: { id: string | null }) {
  const { t } = useI18n();
  const name = useName(id);
  return <span className="text-body font-bold">{id ? name : t('custpick.walk_in')}</span>;
}

export function OrdersScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const nav = useDeviceNav();
  const state = useView(views.orders());
  return (
    <Screen title={t('orders.title')} sub={t('orders.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="flex flex-col gap-3">
            <div className="flex gap-2">
              {Object.entries(v.by_status).map(([s, n]) => (
                <Pill key={s} tone="sky">
                  {t(`order_status.${s}`)} · {n}
                </Pill>
              ))}
            </div>
            {v.orders.map((o) => (
              <Card
                key={o.id}
                onClick={() => nav(`order/${o.id}`)}
                className="flex items-center gap-4 p-5"
                attention={o.status === 'draft'}
              >
                <Pill tone={o.channel === 'whatsapp' ? 'green' : 'sky'}>{t(`channel.${o.channel}`)}</Pill>
                <span className="text-body font-bold">{o.patron_name ?? t('custpick.walk_in')}</span>
                <span className="text-meta text-ink-3">
                  {t('park.lines', { n: o.lines })} · {time(o.created_at)}
                </span>
                <span className="ml-auto text-meta font-semibold">{t(`order_status.${o.status}`)}</span>
                <Money paise={o.total_paise} className="text-arth font-bold" />
              </Card>
            ))}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function OrderScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.order(param ?? 'latest'));
  return (
    <Screen title={t('order.title')} sub={t('order.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_340px] gap-5">
            <Card className="p-6">
              {v.order.lines.map((l) => (
                <div key={l.id} className="flex items-center gap-3 border-b border-line py-3">
                  <span className="flex-1">
                    <span className="block text-body font-semibold">{l.text}</span>
                    {l.check && (
                      <span className="flex items-center gap-1 text-meta text-amber-text">
                        <CircleAlert size={14} /> {t('order.check_line')}
                      </span>
                    )}
                  </span>
                  <span className="num text-meta text-ink-3">× {qty(l.qty_milli)}</span>
                  <Money paise={l.amount_paise} className="w-24 text-right font-bold" />
                </div>
              ))}
              <div className="mt-3 flex justify-between text-arth font-bold">
                <span>{t('paid.total')}</span>
                <Money paise={v.order.total_paise} />
              </div>
            </Card>
            <div className="flex flex-col gap-3">
              <Card className="p-5">
                <SectionTitle>{t('order.pick_list')}</SectionTitle>
                {v.pick_list.map((p) => (
                  <p key={p.item_id} className="text-body">
                    {p.name} × {qty(p.qty_milli)}
                  </p>
                ))}
              </Card>
              <div className="flex items-center gap-2">
                <TierChip tier="R3" />
                <span className="text-meta text-ink-3">{t('order.standing_note')}</span>
              </div>
              <Button size="lg" onClick={() => void run('orders.accept', { order_id: v.order.id })}>
                {t('order.accept')}
              </Button>
              <Button variant="ghost" onClick={() => void run('orders.substitute', { order_id: v.order.id })}>
                {t('order.substitute')}
              </Button>
              <Button
                variant="ghost"
                className="text-red"
                onClick={() =>
                  void run('orders.decline', { order_id: v.order.id, reason_key: 'order.out_of_stock' })
                }
              >
                {t('order.decline')}
              </Button>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}
