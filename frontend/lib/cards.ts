// Card registry rules (I4, SRF-1, SRF-4): which audiences each envelope card type may render for. A surface
// passes its audience; cards for any other audience are dropped before render.
import type { Card, Envelope } from './contracts/envelope';

export type Audience = 'owner' | 'customer';
export type CardType = Card['type'];

/** Card types that may ever reach the customer display. Everything else is owner-only. */
const CUSTOMER_SAFE: ReadonlySet<CardType> = new Set<CardType>(['bill', 'offer', 'receipt']);

export const CARD_TYPES: readonly CardType[] = [
  'bill',
  'hint',
  'approval',
  'batch',
  'verdict',
  'chart',
  'forecast',
  'brief',
  'offer',
  'plan',
  'campaign',
  'patron',
  'stock',
  'po',
  'quote_compare',
  'claim',
  'memory',
  'draft',
  'capital',
  'nudge',
  'pipeline',
  'receipt',
  'health',
];

export function audiencesFor(type: CardType): readonly Audience[] {
  return CUSTOMER_SAFE.has(type) ? ['owner', 'customer'] : ['owner'];
}

/**
 * The cards a surface may render. A card's own audience overrides the envelope's; "all" still has to pass
 * the type rule, so an owner-only type (a hint, a khata balance) never reaches a customer, whatever it says.
 */
export function cardsFor(surface: Audience, envelope: Pick<Envelope, 'audience' | 'cards'>): Card[] {
  return envelope.cards.filter((card) => {
    const audience = card.audience ?? envelope.audience;
    if (audience !== 'all' && audience !== surface) return false;
    return audiencesFor(card.type).includes(surface);
  });
}
