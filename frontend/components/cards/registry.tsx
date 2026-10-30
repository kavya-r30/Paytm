'use client';

// Card components for every envelope card type (C4). Per-type schemas arrive with the layers that produce
// them, so each component reads the base fields plus the optional fields its type is expected to carry.
import {
  BarChart3,
  Bell,
  Boxes,
  Brain,
  FileText,
  Gift,
  HeartPulse,
  Landmark,
  Lightbulb,
  ListChecks,
  Megaphone,
  MessageSquareText,
  PackageCheck,
  Receipt,
  Scale,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Truck,
  UserRound,
  Workflow,
  type LucideIcon,
} from 'lucide-react';
import type { ComponentType } from 'react';
import { cardsFor, type Audience, type CardType } from '@/lib/cards';
import type { Card as EnvelopeCard, Envelope } from '@/lib/contracts/envelope';
import { useI18n } from '@/lib/i18n/react';
import { ArthNote } from '../arth/orb';
import { Card, Money, Pill, TierChip } from '../ui/kit';

type CardProps = { card: EnvelopeCard & Record<string, unknown> };

const ICONS: Record<CardType, LucideIcon> = {
  bill: Receipt,
  hint: Lightbulb,
  approval: ShieldCheck,
  batch: ListChecks,
  verdict: Scale,
  chart: BarChart3,
  forecast: TrendingUp,
  brief: Sparkles,
  offer: Gift,
  plan: Workflow,
  campaign: Megaphone,
  patron: UserRound,
  stock: Boxes,
  po: Truck,
  quote_compare: Scale,
  claim: PackageCheck,
  memory: Brain,
  draft: MessageSquareText,
  capital: Landmark,
  nudge: Bell,
  pipeline: Workflow,
  receipt: FileText,
  health: HeartPulse,
};

function num(v: unknown): number | null {
  return typeof v === 'number' && Number.isFinite(v) ? v : null;
}
function str(v: unknown): string | null {
  return typeof v === 'string' && v ? v : null;
}

/** Generic card body: title by type, the amount if any, Arth's note in the sky band, the tier if gated. */
function BaseCard({ card }: CardProps) {
  const { t } = useI18n();
  const Icon = ICONS[card.type];
  const amount = num(card.amount_paise) ?? num(card.total_paise);
  const title = str(card.title) ?? t(`card.${card.type}`);
  const tier = str(card.tier);
  return (
    <Card className="fade-up flex flex-col gap-3 p-5" attention={!!tier && tier !== 'R0' && tier !== 'R1'}>
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-ground bg-sky text-midnight">
          <Icon size={20} />
        </span>
        <p className="min-w-0 flex-1 truncate text-body font-bold text-ink">{title}</p>
        {tier && <TierChip tier={tier} />}
        {amount !== null && <Money paise={amount} className="text-arth font-bold" />}
      </div>
      {str(card.summary) && <p className="text-body text-ink-2">{str(card.summary)}</p>}
      {card.note && <ArthNote>{card.note}</ArthNote>}
    </Card>
  );
}

function HintCard({ card }: CardProps) {
  const { t } = useI18n();
  return (
    <div className="fade-up flex items-center gap-3 rounded-ground border-2 border-paytm-blue bg-white p-4">
      <p className="min-w-0 flex-1 text-body text-ink">
        <span className="font-bold text-midnight">{t('arth.name')}: </span>
        {card.note ?? t(str(card.reason_key) ?? 'card.hint')}
      </p>
      {num(card.price_paise) !== null && (
        <Pill tone="sky">
          + <Money paise={num(card.price_paise)!} />
        </Pill>
      )}
    </div>
  );
}

function VerdictCard({ card }: CardProps) {
  const { t } = useI18n();
  const verdict = str(card.verdict) ?? 'unclear';
  return (
    <Card className="flex flex-col gap-2 p-5">
      <Pill tone={verdict === 'received' ? 'green' : verdict === 'not_received' ? 'red' : 'amber'}>
        {t(`verdict.${verdict}`)}
      </Pill>
      <p className="text-meta text-ink-3">{t('sentinel.ledger_only')}</p>
    </Card>
  );
}

export const CARD_COMPONENTS: Record<CardType, ComponentType<CardProps>> = {
  bill: BaseCard,
  hint: HintCard,
  approval: BaseCard,
  batch: BaseCard,
  verdict: VerdictCard,
  chart: BaseCard,
  forecast: BaseCard,
  brief: BaseCard,
  offer: BaseCard,
  plan: BaseCard,
  campaign: BaseCard,
  patron: BaseCard,
  stock: BaseCard,
  po: BaseCard,
  quote_compare: BaseCard,
  claim: BaseCard,
  memory: BaseCard,
  draft: BaseCard,
  capital: BaseCard,
  nudge: BaseCard,
  pipeline: BaseCard,
  receipt: BaseCard,
  health: BaseCard,
};

/** Renders an envelope's cards for one surface audience, dropping every card that surface may not show. */
export function CardStack({
  envelope,
  audience,
}: {
  envelope: Pick<Envelope, 'audience' | 'cards'>;
  audience: Audience;
}) {
  return (
    <div className="flex flex-col gap-3">
      {cardsFor(audience, envelope).map((card, i) => {
        const Comp = CARD_COMPONENTS[card.type];
        return <Comp key={card.id ?? i} card={card as CardProps['card']} />;
      })}
    </div>
  );
}
