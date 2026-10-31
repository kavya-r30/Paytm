// Customer display state (I7 CUSTD) derived from the newest relevant domain event for the current bill.
export type CustState = 'idle' | 'amount' | 'pending' | 'paid' | 'reward' | 'preorder';
export const CUST_STATES: CustState[] = ['idle', 'amount', 'pending', 'paid', 'reward', 'preorder'];

type Payload = { bill_id?: string; amount_paise?: number; total_paise?: number };

/** Items are newest first (the stream store prepends). */
export function deriveState(items: { type: string; data: Record<string, unknown> }[]): {
  state: CustState;
  billId: string | null;
  amount: number | null;
} {
  for (const item of items) {
    const p = (item.data.payload ?? {}) as Payload;
    if (item.type === 'offer.issued')
      return { state: 'reward', billId: null, amount: p.amount_paise ?? null };
    if (item.type === 'bill.paid')
      return { state: 'paid', billId: p.bill_id ?? null, amount: p.total_paise ?? null };
    if (item.type === 'payment.pending') return { state: 'pending', billId: p.bill_id ?? null, amount: null };
    if (item.type === 'bill.changed') return { state: 'amount', billId: p.bill_id ?? null, amount: null };
  }
  return { state: 'idle', billId: null, amount: null };
}
