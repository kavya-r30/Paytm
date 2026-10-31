/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Event Spine topic bill.ticket_changed (spec Part C5).
 */
export interface BillTicketChanged {
  event_id: string;
  type: "bill.ticket_changed";
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
    ticket_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    bill_id: string;
    token: number;
    status: "new" | "preparing" | "ready" | "served";
  };
}
/**
 * This interface was referenced by `BillTicketChanged`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
