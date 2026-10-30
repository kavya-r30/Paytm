/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic message.out (spec Part C5).
 */
export interface MessageOut {
  event_id: string;
  type: "message.out";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    thread_ref: string;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    template: string;
    params: {
      [k: string]: unknown;
    };
    category: "utility" | "marketing" | "service";
  };
}
/**
 * This interface was referenced by `MessageOut`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
