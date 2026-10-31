'use client';

// J4 · Stock: SCR-STOCK, SCR-ITEM, SCR-EXPIRY, SCR-SUPPLIERS, SCR-PO, SCR-GATE, SCR-GRN, SCR-CLAIM.
import { AlertTriangle, Camera, Check, PackageCheck, Star, Truck } from 'lucide-react';
import { useState } from 'react';
import { ArthNote } from '@/components/arth/orb';
import { Screen, Sheet, useDeviceNav } from '@/components/shell/device';
import { CoverBar, Sparkline } from '@/components/ui/charts';
import { Button, Card, Chip, Money, Pill, SectionTitle, TierChip, cx } from '@/components/ui/kit';
import { useCommand, useDecide } from '@/lib/api/commands';
import { useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import { IDS } from '@/lib/fixtures/gupta';
import { qty } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, field, type ScreenProps } from './common';
import { useGateText } from './today';

function Name({ id, className }: { id: string | null | undefined; className?: string }) {
  return <span className={className}>{useName(id)}</span>;
}

export function StockScreen(_: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const state = useView(views.stock());
  const expiry = useView(views.expiry());
  return (
    <Screen
      title={t('stock.title')}
      sub={
        state.data
          ? t('stock.sub', {
              n: state.data.items.length,
              k: state.data.items.filter((i) => i.status === 'low' || i.status === 'out').length,
            })
          : undefined
      }
      right={
        <Button
          variant="dark"
          icon={<PackageCheck size={18} />}
          onClick={() => nav(state.mode === 'fixture' ? `grn/${IDS.PO_ID}` : 'grn')}
        >
          {t('stock.goods_in')}
        </Button>
      }
      chips={[
        { label: t('stock.chip_running_out'), text: 'Kya khatam hone wala hai?' },
        { label: t('stock.chip_expiry'), text: 'Expiry is hafte' },
      ]}
    >
      <ViewGate state={state}>
        {(s) => (
          <div className="grid grid-cols-[1fr_330px] gap-5">
            <Card className="divide-y divide-line">
              {s.items.map((i) => {
                const target = i.target_qty_milli || i.on_hand_qty_milli;
                const cover = target ? i.on_hand_qty_milli / target : 1;
                const r = i.status === 'untracked' ? 'ok' : i.status;
                const exp = i.batches
                  .map((b) => b.expires_on)
                  .filter(Boolean)
                  .sort()[0];
                return (
                  <button
                    key={i.item_id}
                    type="button"
                    onClick={() => nav(`item/${i.item_id}`)}
                    className="grid w-full grid-cols-[1fr_180px_110px] items-center gap-4 px-5 py-3.5 text-left"
                  >
                    <span className="min-w-0">
                      <span className="block truncate text-body font-bold">{i.name}</span>
                      <span
                        className={cx(
                          'flex items-center gap-1 text-meta',
                          r === 'ok' ? 'text-ink-3' : 'text-amber-text',
                        )}
                      >
                        {r !== 'ok' && <AlertTriangle size={13} />}
                        {r === 'ok'
                          ? t('stock.status_ok')
                          : r === 'low'
                            ? t('stock.status_low')
                            : t('stock.status_out')}
                        {exp ? ` · ${t('stock.expires', { date: exp })}` : ''}
                      </span>
                    </span>
                    <CoverBar value={cover} risk={r} />
                    <span className="num text-right text-body font-semibold">
                      {qty(i.on_hand_qty_milli)} / {qty(target)}
                    </span>
                  </button>
                );
              })}
            </Card>
            <div className="flex flex-col gap-4">
              {/* The Curator/Procurement suggestion and claim come from L5 playbooks; live shows them then. */}
              {state.mode === 'fixture' && (
                <Card attention className="flex flex-col gap-3 p-5">
                  <SectionTitle>{t('stock.suggestion_title')}</SectionTitle>
                  <ArthNote label={false}>
                    {t('stock.suggestion_body', { festival: t('festival.diwali') })}
                  </ArthNote>
                  <Button onClick={() => nav(`gate/${IDS.GATES.po.gate}`)}>{t('stock.see_rates')}</Button>
                  <Button variant="ghost" onClick={() => nav(`po/${IDS.PO_ID}`)}>
                    {t('stock.make_po')}
                  </Button>
                </Card>
              )}
              <Card className="flex flex-col gap-2 p-5">
                <SectionTitle>{t('stock.exceptions')}</SectionTitle>
                {state.mode === 'fixture' && (
                  <button
                    type="button"
                    onClick={() => nav(`claim/${IDS.CLAIM_ID}`)}
                    className="flex items-center gap-2 text-left text-body"
                  >
                    <Truck size={18} className="text-red" /> {t('stock.claim_short')}
                  </button>
                )}
                {(expiry.data?.batches ?? [])
                  .filter((b) => (b.days_to_expiry ?? 99) <= 7)
                  .map((b) => (
                    <button
                      key={b.batch_id}
                      type="button"
                      onClick={() => nav('expiry')}
                      className="flex items-center gap-2 text-left text-body"
                    >
                      <AlertTriangle size={18} className="text-amber" />
                      {b.name} · {t('stock.days_left', { n: b.days_to_expiry ?? 0 })}
                    </button>
                  ))}
              </Card>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function ItemScreen({ param }: ScreenProps) {
  const { t, money } = useI18n();
  const run = useCommand();
  const state = useView(views.item(param ?? ''));
  const [price, setPrice] = useState<number | null>(null);
  return (
    <Screen title={state.data?.names.en ?? t('item.title')} sub={t('item.sub')}>
      <ViewGate state={state}>
        {(i) => (
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-5">
              <SectionTitle>{t('item.names')}</SectionTitle>
              {Object.entries(i.names).map(([l, n]) => (
                <p key={l} className="text-body">
                  <span className="text-meta text-ink-3">{l}</span> {n}
                </p>
              ))}
              <p className="mt-2 text-meta text-ink-3">SKU {i.sku}</p>
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('item.price')}</SectionTitle>
              <Money paise={price ?? i.price_paise} className="text-3xl font-extrabold" />
              <div className="mt-3 flex gap-2">
                <Button variant="tint" size="sm" onClick={() => setPrice((price ?? i.price_paise) + 100)}>
                  +₹1
                </Button>
                <Button variant="tint" size="sm" onClick={() => setPrice((price ?? i.price_paise) - 100)}>
                  −₹1
                </Button>
              </div>
              {price !== null && price !== i.price_paise && (
                <Button
                  className="mt-3 w-full"
                  onClick={() => void run('catalog.change_price', { item_id: i.id, price_paise: price })}
                >
                  {t('item.save_price', { price: money(price) })} · R2
                </Button>
              )}
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('item.sales')}</SectionTitle>
              <Sparkline
                values={[4, 6, 5, 8, 7, 9, 12]}
                width={220}
                height={60}
                color="var(--color-paytm-blue)"
              />
            </Card>
            <Card className="col-span-3 flex items-center gap-3 p-5">
              <TierChip tier="R4" />
              <span className="text-body text-ink-2">{t('item.bulk_console')}</span>
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function ExpiryScreen(_: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.expiry());
  return (
    <Screen title={t('expiry.title')} sub={t('expiry.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="flex flex-col gap-3">
            {v.batches.map((b) => {
              const d = b.days_to_expiry ?? 999;
              return (
                <Card key={b.batch_id} className="flex items-center gap-4 p-5" attention={d <= 7}>
                  <span className="flex-1 text-body font-bold">{b.name}</span>
                  <span className="num text-meta text-ink-3">× {qty(b.qty_milli)}</span>
                  <Pill tone={b.recalled ? 'red' : d <= 7 ? 'amber' : 'grey'}>
                    {b.recalled ? t('expiry.recalled') : t('stock.days_left', { n: d })}
                  </Pill>
                  {d <= 7 && (
                    <div className="flex gap-2">
                      <Button variant="tint" size="sm">
                        {t('expiry.bundle')}
                      </Button>
                      <Button variant="ghost" size="sm">
                        {t('expiry.return')}
                      </Button>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function SuppliersScreen(_: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const state = useView(views.suppliers());
  return (
    <Screen title={t('suppliers.title')} sub={t('suppliers.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-2 gap-4">
            {v.suppliers.map((s) => (
              <Card
                key={s.id}
                className="flex flex-col gap-2 p-5"
                onClick={() => s.open_pos && nav(state.mode === 'fixture' ? `po/${IDS.PO_ID}` : 'po')}
              >
                <p className="text-arth font-bold">{s.name}</p>
                <p className="text-meta text-ink-3">
                  {t('suppliers.lead', { n: s.lead_days })} · {t(`lang.${s.lang}`)}
                </p>
                <div className="flex gap-2">
                  <Pill tone="sky">{t('suppliers.open_pos', { n: s.open_pos })}</Pill>
                  {s.payable_paise > 0 && (
                    <Pill tone="red">
                      {t('suppliers.payable')} <Money paise={s.payable_paise} />
                    </Pill>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function PoScreen({ param }: ScreenProps) {
  const { t, date } = useI18n();
  const state = useView(views.po(param ?? IDS.PO_ID));
  const STEPS = ['draft', 'placed', 'confirmed', 'received', 'paid'];
  return (
    <Screen title={t('po.title')} sub={state.data ? t('po.sub', { supplier: '' }) : undefined}>
      <ViewGate state={state}>
        {(v) => (
          <div className="flex flex-col gap-4">
            <Card className="flex items-center gap-2 p-4">
              {STEPS.map((s, i) => (
                <div key={s} className="flex flex-1 items-center gap-2">
                  <span
                    className={cx(
                      'flex h-7 w-7 items-center justify-center rounded-chip text-meta font-bold',
                      STEPS.indexOf(v.po.status) >= i ? 'bg-midnight text-white' : 'bg-line text-ink-3',
                    )}
                  >
                    {STEPS.indexOf(v.po.status) > i ? <Check size={14} /> : i + 1}
                  </span>
                  <span className="text-meta">{t(`po.state_${s}`)}</span>
                </div>
              ))}
            </Card>
            <Card className="p-5">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-arth font-bold">{v.po.supplier_name}</span>
                {v.po.due_on && (
                  <Pill tone="sky">{t('po.due', { date: date(`${v.po.due_on}T00:00:00Z`) })}</Pill>
                )}
              </div>
              {v.po.lines.map((l) => (
                <div
                  key={l.item_id}
                  className="grid grid-cols-[1fr_80px_120px_110px] items-center border-b border-line py-2.5 text-body"
                >
                  <span className="font-semibold">{l.name}</span>
                  <span className="num text-ink-3">× {qty(l.qty_milli)}</span>
                  <span className="num text-meta text-ink-3">
                    <Money paise={l.unit_price_paise} />
                    {l.last_price_paise && l.last_price_paise > l.unit_price_paise && (
                      <span className="ml-1 text-green">▼</span>
                    )}
                  </span>
                  <Money paise={l.amount_paise} className="text-right font-bold" />
                </div>
              ))}
              <div className="mt-3 flex justify-between text-arth font-bold">
                <span>{t('paid.total')}</span>
                <Money paise={v.po.total_paise} />
              </div>
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

type Quote = {
  supplier_id: string;
  total_paise: number;
  credit_days: number;
  delivery: string;
  reliability_bp: number;
  recommended: boolean;
};
type ScopeLine = { item_id: string; qty_milli: number; unit_price_paise: number };

/** SCR-GATE: one decision, generalised from the Approval board. Tier chip comes from the command's tier. */
export function GateScreen({ param }: ScreenProps) {
  const { t, time, money } = useI18n();
  const nav = useDeviceNav();
  const decide = useDecide();
  const gateText = useGateText();
  const state = useView(views.gate(param ?? IDS.GATES.po.gate));
  return (
    <Screen
      title={state.data ? t(`gate_type.${state.data.gate.type}`) : t('gate.title')}
      sub={state.data ? t('gate.sub', { time: time(state.data.gate.expires_at) }) : undefined}
      right={state.data && <TierChip tier={state.data.gate.tier} className="text-body" />}
      chips={[
        { label: t('gate.chip_counter'), text: 'Haan, ₹45 bolo' },
        { label: t('gate.chip_later'), text: 'Baad mein' },
      ]}
    >
      <ViewGate state={state}>
        {(v) => {
          const payload = field<Record<string, unknown>>(v.gate.scope, 'payload', {});
          const quotes = field<Quote[]>(payload, 'quotes', []);
          // only priced item lines (a PO, a credit entry) are listed; other scopes read from the summary
          const lines = field<ScopeLine[]>(payload, 'lines', []).filter(
            (l) =>
              typeof l?.item_id === 'string' &&
              Number.isFinite(l.unit_price_paise) &&
              Number.isFinite(l.qty_milli),
          );
          const summary = gateText(v.gate);
          const note = field(payload, 'note', '');
          const draft = field(payload, 'draft', '');
          const budget = field(payload, 'budget_left_paise', 0);
          const approve = async () => {
            if (await decide(v.gate.thread_id, 'approve')) nav('home');
          };
          return (
            <div className="grid grid-cols-[1fr_340px] gap-5">
              <div className="flex flex-col gap-4">
                <Card className="flex flex-col gap-1 p-5">
                  <p className="text-arth font-bold">{summary.title}</p>
                  <p className="text-body text-ink-3">{summary.sub}</p>
                </Card>
                {quotes.length > 0 && (
                  <div className="grid grid-cols-2 gap-4">
                    {quotes.map((q) => (
                      <Card
                        key={q.supplier_id}
                        className={cx(
                          'flex flex-col gap-2 p-5',
                          q.recommended && 'border-2 border-paytm-blue',
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <Name id={q.supplier_id} className="text-arth font-bold" />
                          {q.recommended && <Pill tone="sky">{t('gate.recommended')}</Pill>}
                        </div>
                        <Money paise={q.total_paise} className="text-3xl font-extrabold" />
                        <p className="text-meta text-ink-3">
                          {t('gate.credit_days', { n: q.credit_days })} · {q.delivery}
                        </p>
                        <p className="flex items-center gap-1 text-meta text-ink-2">
                          <Star size={14} className="text-amber" />{' '}
                          {t('gate.reliability', { pct: Math.round(q.reliability_bp / 100) })}
                        </p>
                      </Card>
                    ))}
                  </div>
                )}
                {note && <ArthNote>{note}</ArthNote>}
                {draft && <p className="rounded-ground bg-green-tint p-4 text-body leading-snug">{draft}</p>}
                {lines.length > 0 && (
                  <Card className="p-5">
                    <SectionTitle>{t('gate.whats_in_it')}</SectionTitle>
                    {lines.map((l, i) => (
                      <div
                        key={`${l.item_id}-${i}`}
                        className="flex justify-between border-b border-line py-2 text-body"
                      >
                        <span>
                          <Name id={l.item_id} /> × {qty(l.qty_milli)}
                        </span>
                        <Money
                          paise={Math.round((l.unit_price_paise * l.qty_milli) / 1000)}
                          className="font-semibold"
                        />
                      </div>
                    ))}
                  </Card>
                )}
              </div>
              <Card attention className="flex flex-col gap-3 self-start p-6">
                <p className="text-body text-ink-2">{t(`gate.explain_${v.gate.tier.toLowerCase()}`)}</p>
                {Object.keys(v.gate.conditions).length > 0 && (
                  <ArthNote label={false}>{t('gate.condition_note')}</ArthNote>
                )}
                {budget > 0 && (
                  <p className="text-meta text-ink-3">{t('gate.budget_left', { amount: money(budget) })}</p>
                )}
                {v.readback_key && (
                  <p className="rounded-ground bg-amber-tint p-3 text-body text-amber-text">
                    {t(v.readback_key)}
                  </p>
                )}
                <Button size="lg" onClick={approve}>
                  {t('gate.approve')}
                </Button>
                <Button variant="ghost" onClick={() => void decide(v.gate.thread_id, 'edit', {})}>
                  {t('gate.edit')}
                </Button>
                <Button
                  variant="text"
                  onClick={() => void decide(v.gate.thread_id, 'snooze').then(() => nav('home'))}
                >
                  {t('gate.snooze')}
                </Button>
                <Button
                  variant="text"
                  className="text-red"
                  onClick={() => void decide(v.gate.thread_id, 'decline').then(() => nav('home'))}
                >
                  {t('gate.decline')}
                </Button>
              </Card>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}

export function GrnScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.grn(param ?? IDS.PO_ID));
  return (
    <Screen title={t('grn.title')} sub={t('grn.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_320px] gap-5">
            <Card className="p-5">
              <div className="grid grid-cols-[1fr_100px_100px_120px] border-b border-line pb-2 text-meta font-semibold text-ink-3">
                <span>{t('grn.item')}</span>
                <span>{t('grn.billed')}</span>
                <span>{t('grn.received')}</span>
                <span />
              </div>
              {v.billed.map((b) => {
                const got = v.received.find((r) => r.item_id === b.item_id)?.qty_milli ?? 0;
                const variance = v.variances.find((x) => x.item_id === b.item_id);
                return (
                  <div
                    key={b.item_id}
                    className="grid grid-cols-[1fr_100px_100px_120px] items-center border-b border-line py-3 text-body"
                  >
                    <Name id={b.item_id} className="font-semibold" />
                    <span className="num">{qty(b.qty_milli)}</span>
                    <span className="num">{qty(got)}</span>
                    {variance ? (
                      <Pill tone="red">
                        <Money paise={variance.delta_paise} /> {t(`grn.var_${variance.kind}`)}
                      </Pill>
                    ) : (
                      <Pill tone="green">
                        <Check size={14} /> {t('grn.match')}
                      </Pill>
                    )}
                  </div>
                );
              })}
            </Card>
            <div className="flex flex-col gap-3">
              <Card className="flex aspect-[4/3] flex-col items-center justify-center gap-2 bg-ground text-ink-3">
                <Camera size={36} />
                <span className="text-meta">{t('grn.bill_photo')}</span>
              </Card>
              <Button
                onClick={() =>
                  void run('supply.receive', {
                    po_id: v.po_id,
                    lines: v.received.map((r) => ({ item_id: r.item_id, qty_milli: r.qty_milli })),
                  })
                }
              >
                {t('grn.receive')}
              </Button>
              {v.variances.length > 0 && (
                <Button
                  variant="ghost"
                  className="text-red"
                  onClick={() => nav(`claim/${v.claim_id ?? IDS.CLAIM_ID}`)}
                >
                  {t('grn.raise_claim')}
                </Button>
              )}
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

/** SCR-CLAIM overlay over the stock screen: the draft goes only after the owner's haan (R3). */
export function ClaimScreen({ param }: ScreenProps) {
  const { t, money } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.claim(param ?? IDS.CLAIM_ID));
  return (
    <>
      <StockScreen />
      <Sheet open onClose={() => nav('stock')} width={860}>
        <ViewGate state={state}>
          {(v) => (
            <div className="grid grid-cols-2">
              <div className="border-r border-line p-6">
                <h2 className="text-title">{t('claim.title')}</h2>
                {v.variances.map((x) => (
                  <div key={x.item_id} className="mt-3 rounded-ground bg-red-tint p-4">
                    <span className="text-body font-bold">{x.name}</span>
                    <p className="num text-meta text-red">
                      {t(`claim.kind_${x.kind}`, { expected: qty(x.expected), actual: qty(x.actual) })} →{' '}
                      {money(x.delta_paise)}
                    </p>
                  </div>
                ))}
              </div>
              <div className="flex flex-col gap-3 p-6 pt-16">
                <span className="text-arth font-bold">{v.supplier_name}</span>
                <p className="rounded-ground bg-green-tint p-4 text-body leading-snug">
                  {t('claim.draft', { amount: money(v.claim.amount_paise) })}
                </p>
                <div className="flex gap-2">
                  <Pill>{t('claim.ev_photo')}</Pill>
                  <Pill>{t('claim.ev_po')}</Pill>
                </div>
                <div className="flex gap-2">
                  <Chip active>{t(`lang.${v.claim.lang}`)}</Chip>
                  <Chip>{t('khata.tone_gentle')}</Chip>
                </div>
                <Button
                  size="lg"
                  onClick={() =>
                    void run('supply.send_claim', { claim_id: v.claim.id }).then(() => nav('stock'))
                  }
                >
                  {t('claim.send')} · R3
                </Button>
                <p className="text-meta text-ink-3">{t('claim.footnote')}</p>
              </div>
            </div>
          )}
        </ViewGate>
      </Sheet>
    </>
  );
}
