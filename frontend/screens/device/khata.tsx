'use client';

// J3 · Khata: SCR-KHATA, SCR-PATRON, SCR-PROMISE.
import { CalendarClock, Eye, MessageCircle, Plus, Wallet } from 'lucide-react';
import { useState } from 'react';
import { MemoryCard } from '@/components/arth/memory';
import { ArthNote } from '@/components/arth/orb';
import { Screen, useDeviceNav } from '@/components/shell/device';
import { Sparkline } from '@/components/ui/charts';
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
import { useCommand } from '@/lib/api/commands';
import { useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import type { KhataAccountView } from '@/lib/contracts';
import { qty } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, type ScreenProps } from './common';

const DAY = 86_400_000;

function ageDays(iso: string, now = Date.parse('2026-10-29T08:40:00Z')): number {
  return Math.max(0, Math.round((now - Date.parse(iso)) / DAY));
}

function oldest(a: KhataAccountView): string | null {
  const open = a.entries.filter((e) => e.status !== 'resolved').map((e) => e.occurred_at);
  return open.length ? open.sort()[0]! : null;
}

/** DraftWithTone (I4): the reminder draft in the patron's language with tone tabs. */
function ReminderDraft({ account }: { account: KhataAccountView }) {
  const { t, money } = useI18n();
  const [tone, setTone] = useState<'gentle' | 'firm'>('gentle');
  const run = useCommand();
  return (
    <div className="rounded-ground border border-line p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-meta font-semibold text-ink-3">{t('khata.draft_title')}</span>
        <div className="flex gap-1.5">
          {(['gentle', 'firm'] as const).map((k) => (
            <Chip key={k} active={tone === k} onClick={() => setTone(k)} className="h-8 px-3 text-meta">
              {t(`khata.tone_${k}`)}
            </Chip>
          ))}
        </div>
      </div>
      <p className="rounded-ground bg-green-tint p-3 text-body leading-snug">
        {t(`khata.draft_${tone}`, { name: account.display_name, amount: money(account.balance_paise) })}
      </p>
      <p className="mt-2 flex items-center gap-1.5 text-meta text-ink-3">
        <CalendarClock size={14} /> {t('khata.draft_when')}
      </p>
      <div className="mt-3 flex gap-2">
        <Button
          className="flex-1"
          icon={<MessageCircle size={18} />}
          onClick={() =>
            void run('ledger.send_reminder', {
              account_id: account.account_id,
              template_key: `reminder.${tone}`,
            })
          }
        >
          {t('khata.send_reminder')}
        </Button>
        <TierChip tier="R3" className="self-center" />
      </div>
    </div>
  );
}

function AccountPanel({ patronId }: { patronId: string }) {
  const { t, date, money } = useI18n();
  const run = useCommand();
  const nav = useDeviceNav();
  const state = useView(views.khataAccount(patronId));
  return (
    <ViewGate state={state}>
      {(a) => (
        <Card className="flex h-full flex-col gap-4 overflow-hidden p-6">
          <div className="flex items-center gap-3">
            <Avatar name={a.display_name} size={52} />
            <div className="min-w-0 flex-1">
              <button
                type="button"
                onClick={() => nav(`patron/${a.patron_id}`)}
                className="text-title hover:underline"
              >
                {a.display_name}
              </button>
              <p className="text-meta text-ink-3">
                {t('khata.limit', { limit: money(a.limit_paise) })} · {t('khata.pattern_monthly')}
              </p>
            </div>
            <Money paise={a.balance_paise} className="text-3xl font-extrabold text-red" />
          </div>
          {a.promises
            .filter((p) => p.status === 'active')
            .map((p) => (
              <ArthNote key={p.id}>
                {t('khata.promise_wait', {
                  amount: money(p.amount_paise),
                  date: date(`${p.due_on}T00:00:00Z`),
                })}
              </ArthNote>
            ))}
          <ul className="no-scrollbar min-h-0 flex-1 divide-y divide-line overflow-y-auto">
            {a.entries.map((e) => (
              <li key={e.id} className="py-2.5">
                <div className="flex justify-between">
                  <span className="text-body font-semibold">{date(e.occurred_at)}</span>
                  <Money paise={e.amount_paise} className="font-bold text-red" />
                </div>
                {e.lines.length > 0 && <EntryLines lines={e.lines} />}
              </li>
            ))}
            {a.payments.map((p) => (
              <li key={p.payment_ref} className="flex justify-between py-2.5">
                <span className="text-body">
                  {date(p.occurred_at)} · {t(`pay.${p.mode}`)}
                </span>
                <Money paise={-p.amount_paise} className="font-bold text-green" />
              </li>
            ))}
          </ul>
          {a.balance_paise > 0 && <ReminderDraft account={a} />}
          <Button
            variant="ghost"
            icon={<Wallet size={18} />}
            onClick={() =>
              void run('ledger.record_payment', {
                account_id: a.account_id,
                amount_paise: a.balance_paise,
                payment_ref: `cash-${Date.now()}`,
                mode: 'cash',
              })
            }
          >
            {t('khata.money_received')} · <TierChip tier="R2" />
          </Button>
        </Card>
      )}
    </ViewGate>
  );
}

function EntryLines({ lines }: { lines: KhataAccountView['entries'][number]['lines'] }) {
  return (
    <p className="truncate text-meta text-ink-3">
      {lines.map((l, i) => (
        <LineName key={i} id={l.item_id} q={l.qty_milli} last={i === lines.length - 1} />
      ))}
    </p>
  );
}

function LineName({ id, q, last }: { id: string | null; q: number; last: boolean }) {
  const name = useName(id);
  return (
    <span>
      {name} × {qty(q)}
      {last ? '' : ', '}
    </span>
  );
}

export function KhataScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const state = useView(views.khata());
  const [discreet, setDiscreet] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const selected = param ?? state.data?.accounts[0]?.patron_id;
  const blur = discreet && !revealed;
  return (
    <Screen
      title={t('khata.title')}
      sub={state.data ? t('khata.sub', { n: state.data.accounts.length }) : undefined}
      right={
        <label className="flex items-center gap-2 text-meta text-ink-3">
          <Eye size={16} /> {t('khata.discreet')}
          <Toggle on={discreet} onChange={setDiscreet} label={t('khata.discreet')} />
        </label>
      }
      chips={[{ label: t('khata.chip_sharma'), text: 'Sharma ji ka hisaab' }]}
    >
      <ViewGate state={state}>
        {(k) => (
          <div className="grid h-full grid-cols-[1fr_440px] gap-5">
            <div className="flex min-h-0 flex-col gap-4">
              <Card className="flex items-center justify-between p-6">
                <div>
                  <p className="text-body text-ink-3">{t('khata.total')}</p>
                  <Money
                    paise={k.balance_paise}
                    className={cx('text-amount font-extrabold text-red', blur && 'discreet')}
                  />
                </div>
                <Button variant="dark" icon={<Plus size={18} />}>
                  {t('khata.new_entry')}
                </Button>
              </Card>
              <Card className="no-scrollbar min-h-0 flex-1 overflow-y-auto">
                {k.accounts.map((a) => {
                  const o = oldest(a);
                  return (
                    <button
                      key={a.account_id}
                      type="button"
                      onClick={() => nav(`khata/${a.patron_id}`)}
                      className={cx(
                        'flex w-full items-center gap-3 border-b border-line px-5 py-3 text-left',
                        selected === a.patron_id && 'bg-sky',
                      )}
                    >
                      <Avatar name={a.display_name} size={42} />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-body font-bold">{a.display_name}</span>
                        <span className="text-meta text-ink-3">
                          {o ? t('khata.oldest', { n: ageDays(o) }) : t('khata.settled')}
                        </span>
                      </span>
                      <span onClick={() => setRevealed(true)}>
                        <Money
                          paise={a.balance_paise}
                          className={cx(
                            'text-arth font-bold',
                            a.balance_paise > 0 ? 'text-red' : 'text-green',
                            blur && 'discreet',
                          )}
                        />
                      </span>
                    </button>
                  );
                })}
              </Card>
            </div>
            {selected && <AccountPanel patronId={selected} />}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function PatronScreen({ param }: ScreenProps) {
  const { t, money } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const id = param ?? '';
  const state = useView(views.patron(id));
  return (
    <Screen title={state.data?.display_name ?? t('patron.title')} sub={t('patron.sub')}>
      <ViewGate state={state}>
        {(p) => (
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-5">
              <SectionTitle>{t('patron.lifecycle')}</SectionTitle>
              <Pill tone="green">{t('patron.state_regular')}</Pill>
              <p className="mt-4 text-meta text-ink-3">{t('patron.rhythm')}</p>
              <Sparkline
                values={[2, 3, 2, 4, 3, 5, 4, 4]}
                width={200}
                height={40}
                color="var(--color-paytm-blue)"
              />
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('patron.rewards')}</SectionTitle>
              <p className="num text-3xl font-extrabold">{p.rewards.stamps}/10</p>
              <p className="text-meta text-ink-3">
                {t('patron.rewards_value', { value: money(p.rewards.available_value_paise) })}
              </p>
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('patron.language')}</SectionTitle>
              <p className="text-arth font-bold">{t(`lang.${p.lang}`)}</p>
              <Button
                variant="text"
                onClick={() => void run('patrons.update_profile', { patron_id: p.patron_id, lang: 'hi' })}
              >
                {t('common.change')}
              </Button>
            </Card>
            <Card className="col-span-2 p-5">
              <SectionTitle>{t('patron.consent')}</SectionTitle>
              {(['receipts', 'reminders', 'marketing'] as const).map((k) => (
                <div key={k} className="flex items-center justify-between border-b border-line py-2.5">
                  <span className="text-body">{t(`patron.consent_${k}`)}</span>
                  <Toggle
                    on={p.consent[k]}
                    onChange={() =>
                      void run('consent.grant', { patron_id: p.patron_id, purpose: k, source_ref: 'counter' })
                    }
                    label={k}
                  />
                </div>
              ))}
              <p className="mt-2 text-meta text-ink-3">{t('patron.consent_note')}</p>
            </Card>
            <div className="flex flex-col gap-3">
              <MemoryCard fact={t('patron.memory_example')} evidence={[t('patron.memory_evidence')]} />
              <Button variant="ghost" onClick={() => nav(`khata/${p.patron_id}`)}>
                {t('patron.open_khata')}
              </Button>
              <Button
                variant="ghost"
                className="text-red"
                onClick={() => void run('privacy.erase_patron', { patron_id: p.patron_id })}
              >
                {t('patron.erase')} · <TierChip tier="R4" />
              </Button>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function PromiseScreen(_: ScreenProps) {
  const { t, date } = useI18n();
  const state = useView(views.promises());
  return (
    <Screen title={t('promise.title')} sub={t('promise.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-2 gap-4">
            {v.promises.map((p) => (
              <Card key={p.id} className="flex items-center gap-4 p-5">
                <CalendarClock className="text-midnight" />
                <span className="flex-1 text-body font-semibold">{date(`${p.due_on}T00:00:00Z`)}</span>
                <Money paise={p.amount_paise} className="text-arth font-bold" />
                <Pill tone={p.status === 'kept' ? 'green' : p.status === 'broken' ? 'red' : 'amber'}>
                  {t(`promise.status_${p.status}`)}
                </Pill>
              </Card>
            ))}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}
