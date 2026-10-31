/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic storefront.published (spec Part C5).
 */
export interface StorefrontPublished {
  event_id: string;
  type: "storefront.published";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: {
    slug: string;
    published: boolean;
  };
}
/**
 * This interface was referenced by `StorefrontPublished`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
