/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic payment.refunded (spec Part C5).
 */
export interface PaymentRefunded {
  event_id: string;
  type: "payment.refunded";
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
    refund_id: string;
    amount_paise: number;
    mode: string;
  };
}
/**
 * This interface was referenced by `PaymentRefunded`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
