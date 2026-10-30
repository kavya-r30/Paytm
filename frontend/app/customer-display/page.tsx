'use client';

// Customer display (I7 CUSTD): 400×200 rear dot display. Renders only audience:customer content; never counter
// hints, khata balances or other customers' data. States follow domain events for the current bill.
import { Check } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { FixedCanvas } from '@/components/shell/frame';
import { cx } from '@/components/ui/kit';
import { useDataMode, useView } from '@/lib/api/hooks';
import { views } from '@/lib/api/views';
import { IDS, home } from '@/lib/fixtures/gupta';
import { useI18n } from '@/lib/i18n/react';
import { useStream } from '@/lib/store/turn';
import { CUST_STATES as CYCLE, deriveState, type CustState } from '@/lib/customer-display';
import { FakeQr } from '@/screens/device/bill';

function Dot({ children, className }: { children: string; className?: string }) {
  return <span className={cx('dot-type num font-extrabold leading-none', className)}>{children}</span>;
}

export default function CustomerDisplay() {
  const { t, money } = useI18n();
  const mode = useDataMode();
  const items = useStream((s) => s.items);
  const [forced, setForced] = useState<CustState | null>(null);
  const [tick, setTick] = useState(0);
  const [since, setSince] = useState(() => Date.now());

  useEffect(() => {
    const q = new URLSearchParams(window.location.search).get('state');
    if (q && (CYCLE as string[]).includes(q)) setForced(q as CustState);
  }, []);
  // Fixture mode walks through every state so the display can be reviewed without a backend.
  useEffect(() => {
    if (mode !== 'fixture' || forced) return;
    const id = window.setInterval(() => setTick((n) => n + 1), 3500);
    return () => window.clearInterval(id);
  }, [mode, forced]);

  const live = useMemo(() => deriveState(items), [items]);
  useEffect(() => setSince(Date.now()), [live.state, live.billId]);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const state: CustState =
    forced ??
    (mode === 'fixture'
      ? CYCLE[tick % CYCLE.length]!
      : (live.state === 'paid' || live.state === 'reward') && now - since > 20_000
        ? 'idle'
        : live.state);
  const billId = mode === 'fixture' ? IDS.BILL_ID : live.billId;
  const pay = useView(views.billPay(billId ?? 'none'), { enabled: !!billId });
  const amount = live.amount ?? pay.data?.bill.total_paise ?? 0;
  const shop = home.greeting.shop_name;
  const billNo = (billId ?? '').slice(-4);

  return (
    <FixedCanvas width={400} height={200} className="bg-midnight text-white" letterbox="bg-ink">
      <div className="flex h-full flex-col p-4">
        <div className="flex justify-between text-meta text-white/70">
          <span>{shop}</span>
          {state !== 'idle' && state !== 'reward' && billNo && <span>{t('cust.bill', { n: billNo })}</span>}
        </div>
        {state === 'idle' && (
          <div className="flex flex-1 flex-col">
            <p className="mt-1 text-body font-bold">{t('cust.idle_offer')}</p>
            <p className="text-meta text-white/70">{t('cust.idle_offer_sub')}</p>
            <div className="mt-auto flex items-end justify-between">
              <Dot className="text-4xl text-amber">{money(54900)}</Dot>
              <span className="text-meta text-white/70">
                {t('cust.preorder_deposit', { amount: money(10000) })}
              </span>
            </div>
          </div>
        )}
        {state === 'amount' && (
          <div className="flex flex-1 items-end justify-between gap-3">
            <Dot className="self-start pt-1 text-5xl">{money(amount)}</Dot>
            <div className="flex items-center gap-2">
              <span className="rounded-ground bg-white p-1">
                <FakeQr seed={billId ?? 'qr'} size={84} />
              </span>
              <span className="w-24 text-meta leading-tight text-white/80">{t('cust.scan_any')}</span>
            </div>
          </div>
        )}
        {state === 'pending' && (
          <div className="flex flex-1 flex-col justify-center gap-2">
            <Dot className="text-4xl">{money(amount)}</Dot>
            <p className="pulse text-body">{t('cust.pending')}</p>
          </div>
        )}
        {state === 'paid' && (
          <div className="flex flex-1 flex-col justify-between">
            <Dot className="text-5xl text-green-fill">{money(amount)}</Dot>
            <p className="flex items-center gap-2 text-body font-bold">
              <span className="flex h-7 w-7 items-center justify-center rounded-chip border-2 border-green-fill text-green-fill">
                <Check size={16} />
              </span>
              {t('cust.paid')}
            </p>
            <div className="flex items-center gap-1.5 text-meta text-white/70">
              {Array.from({ length: 10 }, (_, i) => (
                <span
                  key={i}
                  className={cx('h-2 w-2 rounded-chip', i < 4 ? 'bg-paytm-blue' : 'bg-white/20')}
                />
              ))}
            </div>
          </div>
        )}
        {state === 'reward' && (
          <div className="flex flex-1 flex-col">
            <p className="text-body font-bold text-green-fill">{t('cust.cashback')}</p>
            <Dot className="text-5xl text-green-fill">{money(live.amount ?? 2500)}</Dot>
            <p className="mt-auto rounded-ground bg-white/10 px-3 py-1.5 text-meta">{t('cust.next_offer')}</p>
          </div>
        )}
        {state === 'preorder' && (
          <div className="flex flex-1 flex-col justify-center gap-1">
            <p className="text-body font-bold text-amber">{t('cust.preorder_booked')}</p>
            <Dot className="text-3xl">{money(10000)}</Dot>
            <p className="text-meta text-white/70">{t('cust.preorder_collect')}</p>
          </div>
        )}
      </div>
    </FixedCanvas>
  );
}
