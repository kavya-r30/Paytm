'use client';

// J7 · Entry: SCR-ONB (5 steps), SCR-PIN, SCR-SHIFT. J8 · Packs: SCR-KOT, SCR-APPT, SCR-RX.
import { Check, Coffee, Delete, Pill as PillIcon, Scissors, Store } from 'lucide-react';
import { useState } from 'react';
import { ArthNote, Orb } from '@/components/arth/orb';
import { Screen, useDeviceNav } from '@/components/shell/device';
import { Avatar, Button, Card, Chip, Money, Pill, SectionTitle, cx } from '@/components/ui/kit';
import { deviceCredential, login } from '@/lib/api/client';
import { useCommand } from '@/lib/api/commands';
import { useDataMode, useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import { NATIVE_NAME, qty, type UiLocale } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, type ScreenProps } from './common';

const PACKS = [
  { id: 'kirana', icon: Store },
  { id: 'cafe', icon: Coffee },
  { id: 'pharmacy', icon: PillIcon },
  { id: 'salon', icon: Scissors },
] as const;

export function OnboardingScreen(_: ScreenProps) {
  const { t, setLocale } = useI18n();
  const run = useCommand();
  const state = useView(views.onboarding());
  const [step, setStep] = useState<string | null>(null);
  const [pack, setPack] = useState('kirana');
  return (
    <Screen title={t('onb.title')} sub={t('onb.sub')}>
      <ViewGate state={state}>
        {(v) => {
          const current = step ?? v.next_step ?? v.steps[0]!;
          const next = () => {
            void run('onboarding.complete_step', { step: current });
            const i = v.steps.indexOf(current);
            setStep(v.steps[Math.min(i + 1, v.steps.length - 1)]!);
          };
          return (
            <div className="flex flex-col gap-5">
              <div className="flex gap-2">
                {v.steps.map((s, i) => (
                  <div key={s} className="flex flex-1 items-center gap-2">
                    <span
                      className={cx(
                        'flex h-8 w-8 items-center justify-center rounded-chip text-meta font-bold',
                        v.completed.includes(s)
                          ? 'bg-green-fill text-white'
                          : s === current
                            ? 'bg-midnight text-white'
                            : 'bg-line text-ink-3',
                      )}
                    >
                      {v.completed.includes(s) ? <Check size={16} /> : i + 1}
                    </span>
                    <span className="text-meta font-semibold">{t(`onb.step_${s}`)}</span>
                  </div>
                ))}
              </div>
              <Card className="flex min-h-[340px] flex-col gap-5 p-8">
                <h2 className="text-title">{t(`onb.q_${current}`)}</h2>
                {current === 'language' && (
                  <div className="grid grid-cols-4 gap-3">
                    {(['hi', 'hi-Latn', 'en', 'mr', 'ta', 'bn', 'gu', 'te'] as UiLocale[]).map((l) => (
                      <Chip key={l} onClick={() => setLocale(l)}>
                        {NATIVE_NAME[l]}
                      </Chip>
                    ))}
                  </div>
                )}
                {current === 'pack' && (
                  <div className="grid grid-cols-4 gap-3">
                    {PACKS.map(({ id, icon: Icon }) => (
                      <button
                        key={id}
                        type="button"
                        onClick={() => setPack(id)}
                        className={cx(
                          'flex h-32 flex-col items-center justify-center gap-2 rounded-card border-2',
                          pack === id ? 'border-paytm-blue bg-sky' : 'border-line bg-white',
                        )}
                      >
                        <Icon size={32} />
                        <span className="text-body font-bold">{t(`pack.${id}`)}</span>
                      </button>
                    ))}
                  </div>
                )}
                {current === 'details' && (
                  <div className="grid grid-cols-2 gap-3">
                    {['onb.shop_name', 'onb.city', 'onb.hours', 'onb.upi'].map((k) => (
                      <input
                        key={k}
                        placeholder={t(k)}
                        className="h-12 rounded-ground border border-line px-4 text-body"
                      />
                    ))}
                  </div>
                )}
                {current === 'catalog' && (
                  <div className="grid grid-cols-3 gap-3">
                    {['starter', 'photo', 'scan'].map((k) => (
                      <Card
                        key={k}
                        className="flex h-28 items-center justify-center p-4 text-center text-body font-bold"
                        onClick={next}
                      >
                        {t(`onb.catalog_${k}`)}
                      </Card>
                    ))}
                  </div>
                )}
                {current === 'people' && <ArthNote>{t('onb.people_note')}</ArthNote>}
                <Button size="lg" className="mt-auto self-end" onClick={next}>
                  {t('onb.next')}
                </Button>
              </Card>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}

/** SCR-PIN: staff avatars and a PIN pad. Live mode logs in with the device credential from the seed. */
export function PinScreen(_: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const mode = useDataMode();
  const state = useView(views.staffLogin());
  const [who, setWho] = useState<string | null>(null);
  const [pin, setPin] = useState('');
  const [credential, setCredential] = useState(() =>
    typeof window === 'undefined' ? '' : (deviceCredential() ?? ''),
  );
  const [error, setError] = useState<string | null>(null);
  const press = async (d: string) => {
    const next = (pin + d).slice(0, 4);
    setPin(next);
    if (next.length === 4 && who) {
      if (mode === 'fixture' && !credential) {
        nav('home');
        return;
      }
      try {
        await login(credential, who, next, 'device');
        window.location.href = '/device/home';
      } catch {
        setError(t('pin.wrong'));
        setPin('');
      }
    }
  };
  return (
    <Screen title={t('pin.title')} sub={t('pin.sub')} dock={false}>
      <div className="grid grid-cols-2 gap-6">
        <div className="flex flex-col gap-3">
          <ViewGate state={state}>
            {(v) => (
              <div className="grid grid-cols-2 gap-3">
                {v.staff.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setWho(s.id)}
                    className={cx(
                      'flex items-center gap-3 rounded-card border-2 bg-white p-4 text-left',
                      who === s.id ? 'border-paytm-blue' : 'border-transparent',
                    )}
                  >
                    <Avatar name={s.name} />
                    <span>
                      <span className="block text-body font-bold">{s.name}</span>
                      <span className="text-meta text-ink-3">{t(`role.${s.role}`)}</span>
                    </span>
                  </button>
                ))}
              </div>
            )}
          </ViewGate>
          <label className="mt-2 text-meta text-ink-3">
            {t('pin.credential')}
            <input
              value={credential}
              onChange={(e) => setCredential(e.target.value.trim())}
              className="mt-1 h-10 w-full rounded-ground border border-line px-3 text-meta"
            />
          </label>
          <p className="text-meta text-ink-3">{t('pin.seed_hint')}</p>
        </div>
        <Card className="flex flex-col items-center gap-4 p-6">
          <div className="flex gap-3">
            {[0, 1, 2, 3].map((i) => (
              <span
                key={i}
                className={cx('h-4 w-4 rounded-chip', i < pin.length ? 'bg-midnight' : 'bg-line')}
              />
            ))}
          </div>
          {error && <p className="text-body text-red">{error}</p>}
          <div className="grid grid-cols-3 gap-3">
            {['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫'].map((d) =>
              d ? (
                <button
                  key={d}
                  type="button"
                  disabled={!who}
                  onClick={() => (d === '⌫' ? setPin(pin.slice(0, -1)) : void press(d))}
                  className="num flex h-16 w-20 items-center justify-center rounded-button bg-ground text-title disabled:opacity-40"
                >
                  {d === '⌫' ? <Delete size={22} /> : d}
                </button>
              ) : (
                <span key="blank" />
              ),
            )}
          </div>
        </Card>
      </div>
    </Screen>
  );
}

const DENOMS = [50000, 20000, 10000, 5000, 2000, 1000, 500, 100];

export function ShiftScreen(_: ScreenProps) {
  const { t, money, time } = useI18n();
  const run = useCommand();
  const state = useView(views.shift());
  const [counts, setCounts] = useState<Record<number, number>>({});
  const counted = DENOMS.reduce((s, d) => s + d * (counts[d] ?? 0), 0);
  return (
    <Screen title={t('shift.title')} sub={t('shift.sub')}>
      <ViewGate state={state}>
        {(v) =>
          !v.current ? (
            <Card className="flex flex-col items-center gap-4 p-10">
              <Orb size={72} />
              <p className="text-title">{t('shift.open_q')}</p>
              <Button size="lg" onClick={() => void run('shift.open', { float_paise: 200000 })}>
                {t('shift.open', { float: money(200000) })}
              </Button>
            </Card>
          ) : (
            <div className="grid grid-cols-[1fr_320px] gap-5">
              <Card className="grid grid-cols-2 gap-3 p-5">
                {DENOMS.map((d) => (
                  <label
                    key={d}
                    className="flex items-center justify-between rounded-ground bg-ground px-4 py-2"
                  >
                    <span className="num text-body font-bold">{money(d)}</span>
                    <input
                      type="number"
                      min={0}
                      value={counts[d] ?? ''}
                      onChange={(e) => setCounts((c) => ({ ...c, [d]: Number(e.target.value) }))}
                      className="num h-10 w-20 rounded-ground border border-line px-2 text-right"
                    />
                  </label>
                ))}
              </Card>
              <Card className="flex flex-col gap-3 p-6">
                <p className="text-meta text-ink-3">
                  <Who id={v.current.staff_id} /> · {time(v.current.opened_at)}
                </p>
                <p className="flex justify-between text-body">
                  <span>{t('hisaab.expected')}</span>
                  <Money paise={v.current.expected_paise} className="font-bold" />
                </p>
                <p className="flex justify-between text-body">
                  <span>{t('shift.counted')}</span>
                  <Money paise={counted} className="font-bold" />
                </p>
                <p
                  className={cx(
                    'flex justify-between text-arth font-bold',
                    counted - v.current.expected_paise < 0 ? 'text-red' : 'text-green',
                  )}
                >
                  <span>{t('shift.variance')}</span>
                  <Money paise={counted - v.current.expected_paise} />
                </p>
                <Button
                  size="lg"
                  onClick={() => void run('shift.close', { shift_id: v.current!.id, counted_paise: counted })}
                >
                  {t('shift.close')}
                </Button>
              </Card>
            </div>
          )
        }
      </ViewGate>
    </Screen>
  );
}

function Who({ id }: { id: string | null }) {
  return <span className="font-semibold">{useName(id)}</span>;
}

const KOT_COLUMNS = ['new', 'preparing', 'ready', 'served'] as const;

export function KotScreen(_: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.kot());
  return (
    <Screen title={t('kot.title')} sub={t('kot.sub')} dock={false}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid h-full grid-cols-4 gap-4">
            {KOT_COLUMNS.map((col) => (
              <div key={col} className="flex flex-col gap-3 rounded-card bg-white/60 p-3">
                <p className="px-2 text-body font-bold">{t(`kot.col_${col}`)}</p>
                {v.tickets
                  .filter((tk) => tk.status === col)
                  .map((tk) => (
                    <Card key={tk.id} className="p-4" attention={col === 'new'}>
                      <div className="flex items-center justify-between">
                        <span className="num text-title">#{tk.token}</span>
                        <span
                          className={cx('num text-meta', tk.age_seconds > 480 ? 'text-red' : 'text-ink-3')}
                        >
                          {Math.round(tk.age_seconds / 60)}m
                        </span>
                      </div>
                      {tk.items.map((i, n) => (
                        <p key={n} className="text-body">
                          {qty(i.qty_milli)} × {i.name}
                          {i.modifiers.length > 0 && (
                            <span className="block text-meta text-amber-text">{i.modifiers.join(', ')}</span>
                          )}
                        </p>
                      ))}
                      {col !== 'served' && (
                        <Button
                          variant="tint"
                          size="sm"
                          className="mt-2 w-full"
                          onClick={() => void run('counter.advance_ticket', { ticket_id: tk.id })}
                        >
                          {t(`kot.next_${col}`)}
                        </Button>
                      )}
                    </Card>
                  ))}
              </div>
            ))}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function AppointmentsScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const state = useView(views.appointments());
  return (
    <Screen title={t('appt.title')} sub={t('appt.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_280px] gap-5">
            <div
              className="grid gap-4"
              style={{ gridTemplateColumns: `repeat(${Math.max(v.staff.length, 1)}, minmax(0, 1fr))` }}
            >
              {v.staff.map((s) => (
                <Card key={s.id} className="flex flex-col gap-2 p-4">
                  <p className="text-arth font-bold">{s.name}</p>
                  <p className="text-meta text-ink-3">{s.skills.join(' · ')}</p>
                  {s.appointments.map((a) => (
                    <div
                      key={a.id}
                      className={cx(
                        'rounded-ground p-3',
                        a.status === 'done'
                          ? 'bg-green-tint'
                          : a.status === 'checked_in'
                            ? 'bg-sky'
                            : 'bg-ground',
                      )}
                    >
                      <p className="num text-body font-bold">{a.start_at ? time(a.start_at) : '—'}</p>
                      <p className="text-meta">
                        <Who id={a.patron_id} /> · {t(`appt.status_${a.status}`)}
                      </p>
                    </div>
                  ))}
                </Card>
              ))}
            </div>
            <Card className="flex flex-col gap-3 p-5">
              <SectionTitle>{t('appt.walk_ins', { n: v.walk_ins.length })}</SectionTitle>
              {v.walk_ins.map((w) => (
                <Pill key={w.id} tone="amber">
                  {t(`appt.status_${w.status}`)}
                </Pill>
              ))}
              <p className="text-meta text-ink-3">{t('appt.no_shows', { n: v.no_shows })}</p>
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function RxScreen(_: ScreenProps) {
  const { t, time, date } = useI18n();
  const state = useView(views.rx());
  return (
    <Screen title={t('rx.title')} sub={t('rx.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-5">
              <SectionTitle>{t('rx.sales')}</SectionTitle>
              {v.rx_sales.map((s) => (
                <p key={s.bill_id + s.item_id} className="text-body">
                  {s.name} ·{' '}
                  <span className="text-meta text-ink-3">
                    {t('rx.seen_by')} <Who id={s.staff_id} /> {time(s.occurred_at)}
                  </span>
                </p>
              ))}
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('rx.refills')}</SectionTitle>
              {v.refills_due.map((r) => (
                <p key={r.patron_id + r.item_id} className="text-body">
                  <Who id={r.patron_id} /> · {date(`${r.due_on}T00:00:00Z`)}
                </p>
              ))}
              <p className="mt-2 text-meta text-ink-3">{t('rx.consent_only')}</p>
            </Card>
            <Card className="p-5" attention={v.recalls.length > 0}>
              <SectionTitle>{t('rx.recalls')}</SectionTitle>
              {v.recalls.length === 0 ? (
                <Pill tone="green">{t('rx.no_recalls')}</Pill>
              ) : (
                v.recalls.map((r) => (
                  <Pill key={r.batch_id} tone="red">
                    {r.buyer_ids.length}
                  </Pill>
                ))
              )}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}
