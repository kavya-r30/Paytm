/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic action.snoozed (spec Part C5).
 */
export interface ActionSnoozed {
  event_id: string;
  type: "action.snoozed";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: {
    key: string;
    until: string;
  };
}
/**
 * This interface was referenced by `ActionSnoozed`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
