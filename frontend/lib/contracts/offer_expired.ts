/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic offer.expired (spec Part C5).
 */
export interface OfferExpired {
  event_id: string;
  type: "offer.expired";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: {
    issuance_ids: string[];
  };
}
/**
 * This interface was referenced by `OfferExpired`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
