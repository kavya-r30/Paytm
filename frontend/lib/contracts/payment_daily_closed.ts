/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic payment.daily_closed (spec Part C5).
 */
export interface PaymentDailyClosed {
  event_id: string;
  type: "payment.daily_closed";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: {
    date: string;
  };
}
/**
 * This interface was referenced by `PaymentDailyClosed`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
