'use client';

// J5 · Badhao: SCR-DEMAND, SCR-OFFERS, SCR-OFFER-D, SCR-STOREFRONT (the L6 growth screens are in growth.tsx).
import { Gift, Megaphone, Percent, Printer, Stamp, Wallet } from 'lucide-react';
import { ArthNote } from '@/components/arth/orb';
import { Screen, useDeviceNav } from '@/components/shell/device';
import { FakeQr } from './bill';
import { Ring } from '@/components/ui/charts';
import { Button, Card, Money, Pill, SectionTitle, TierChip, Toggle } from '@/components/ui/kit';
import { useCommand } from '@/lib/api/commands';
import { useView } from '@/lib/api/hooks';
import { views } from '@/lib/api/views';
import type { OffersView } from '@/lib/contracts';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, type ScreenProps } from './common';

export function DemandScreen(_: ScreenProps) {
  const { t, date } = useI18n();
  const nav = useDeviceNav();
  const state = useView(views.demand());
  return (
    <Screen title={t('demand.title')} sub={t('demand.sub')}>
      <ViewGate state={state}>
        {(v) =>
          v.status === 'needs_more_data' ? (
            <ArthNote>{t('demand.needs_more')}</ArthNote>
          ) : (
            <div className="grid grid-cols-[1fr_360px] gap-5">
              <div className="flex flex-col gap-3">
                {v.clusters.map((c) => (
                  <Card key={c.label} className="flex items-center gap-4 p-5">
                    <span className="num flex h-12 w-12 items-center justify-center rounded-ground bg-sky text-arth font-extrabold text-midnight">
                      {c.count}
                    </span>
                    <span className="flex-1">
                      <span className="block text-arth font-bold">{c.label}</span>
                      <span className="text-meta text-ink-3">{t('demand.asked', { n: c.count })}</span>
                    </span>
                    <Button
                      variant="tint"
                      size="sm"
                      // a demanded item has no price yet: the owner sets it on the Learn form (R2 read-back)
                      onClick={() => nav(`learn?name=${encodeURIComponent(c.label)}`)}
                    >
                      {t('demand.add_catalog')} · R2
                    </Button>
                    <Button variant="ghost" size="sm">
                      {t('demand.add_po')}
                    </Button>
                  </Card>
                ))}
              </div>
              <Card className="p-5">
                <SectionTitle>{t('demand.utterances')}</SectionTitle>
                {v.unmet.map((u) => (
                  <p key={u.id} className="border-b border-line py-2 text-body">
                    “{u.text}” <span className="text-meta text-ink-3">· {date(u.occurred_at)}</span>
                  </p>
                ))}
              </Card>
            </div>
          )
        }
      </ViewGate>
    </Screen>
  );
}

const PROGRAM_ICON: Record<string, typeof Gift> = {
  next_txn_cashback: Wallet,
  welcome_coupon: Percent,
  stamps: Stamp,
};

function ProgramRow({ p }: { p: OffersView['programs'][number] }) {
  const { t, money } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const Icon = PROGRAM_ICON[p.type] ?? Gift;
  const used = p.budget_paise ? p.spent_paise / p.budget_paise : 0;
  return (
    <Card className="flex items-center gap-4 p-5">
      <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-ground bg-sky text-midnight">
        <Icon size={22} />
      </span>
      <button type="button" onClick={() => nav(`offer/${p.id}`)} className="min-w-0 flex-1 text-left">
        <span className="block truncate text-body font-bold">{t(`offer_kind.${p.type}`)}</span>
        <span className="block truncate text-meta text-ink-3">
          {t('offers.terms', {
            amount: money(p.terms.amount_paise),
            min: money(p.terms.min_spend_paise),
            days: p.terms.expiry_days,
          })}
        </span>
        <span className="text-meta text-ink-2">
          {t('offers.reach', { issued: p.issued, pct: Math.round(used * 100) })}
        </span>
      </button>
      <Toggle
        on={p.status === 'active'}
        onChange={() => void run('offers.pause_program', { program_id: p.id })}
        label={t('offers.toggle')}
      />
    </Card>
  );
}

export function OffersScreen(_: ScreenProps) {
  const { t, money } = useI18n();
  const state = useView(views.offers());
  return (
    <Screen
      title={t('offers.title')}
      sub={t('offers.sub')}
      chips={[{ label: t('offers.chip_idea'), text: 'Naya offer idea' }]}
    >
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_360px] gap-5">
            <div className="flex flex-col gap-3">
              {v.programs.map((p) => (
                <ProgramRow key={p.id} p={p} />
              ))}
              <p className="text-meta text-ink-3">
                {t('offers.liability', { amount: money(v.liability.outstanding_paise) })}
              </p>
            </div>
            <Card attention className="flex flex-col gap-3 self-start p-6">
              <SectionTitle action={<TierChip tier="R3" />}>{t('offers.new_idea')}</SectionTitle>
              <ArthNote label={false}>{t('offers.idea_pending')}</ArthNote>
              <Button disabled>{t('offers.start')}</Button>
              <Button variant="ghost" disabled>
                {t('offers.see_message')}
              </Button>
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function OfferDetailScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.offer(param ?? ''));
  return (
    <Screen
      title={state.data ? t(`offer_kind.${state.data.program.type}`) : t('offers.title')}
      sub={t('offerd.sub')}
    >
      <ViewGate state={state}>
        {(v) => {
          const p = v.program;
          return (
            <div className="grid grid-cols-3 gap-4">
              <Card className="flex flex-col items-center gap-2 p-5">
                <Ring value={p.budget_paise ? p.spent_paise / p.budget_paise : 0} size={110} />
                <p className="text-meta text-ink-3">
                  <Money paise={p.spent_paise} /> / <Money paise={p.budget_paise} />
                </p>
              </Card>
              <Card className="p-5">
                <SectionTitle>{t('offerd.counts')}</SectionTitle>
                {(['issued', 'redeemed', 'expired', 'outstanding'] as const).map((k) => (
                  <p key={k} className="flex justify-between py-1 text-body">
                    <span>{t(`offerd.${k}`)}</span>
                    <Money paise={p.liability[`${k}_paise`]} className="font-bold" />
                  </p>
                ))}
              </Card>
              <Card className="p-5">
                <SectionTitle>{t('offerd.holdout')}</SectionTitle>
                <p className="num text-3xl font-extrabold">
                  {p.treated} / {p.holdout}
                </p>
                <p className="text-meta text-ink-3">{t('offerd.holdout_note')}</p>
              </Card>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}

export function StorefrontScreen(_: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.storefront());
  return (
    <Screen title={t('storefront.title')} sub={t('storefront.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-2 gap-5">
            <Card className="flex flex-col items-center gap-4 p-6">
              <FakeQr seed={v.slug ?? 'shop'} size={200} />
              <a
                href={v.url ?? `/s/${v.slug ?? ''}`}
                target="_blank"
                rel="noreferrer"
                className="text-arth font-bold text-cyan-text"
              >
                {v.url ?? `/s/${v.slug ?? ''}`}
              </a>
              <div className="flex gap-2">
                <Button icon={<Megaphone size={18} />}>{t('storefront.send_link')} · R3</Button>
                <Button variant="ghost" icon={<Printer size={18} />}>
                  {t('paid.print')}
                </Button>
              </div>
            </Card>
            <Card className="flex flex-col gap-4 p-6">
              <div className="flex items-center justify-between">
                <span className="text-body">{t('storefront.published')}</span>
                <Toggle
                  on={v.published}
                  onChange={(on) =>
                    void run('storefront.publish', {
                      slug: v.slug,
                      published: on,
                      show_offers: v.show_offers,
                    })
                  }
                  label={t('storefront.published')}
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-body">{t('storefront.show_offers')}</span>
                <Toggle
                  on={v.show_offers}
                  onChange={(on) =>
                    void run('storefront.publish', { slug: v.slug, published: v.published, show_offers: on })
                  }
                  label={t('storefront.show_offers')}
                />
              </div>
              <Pill tone="sky">{t('storefront.items', { n: v.items })}</Pill>
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}
