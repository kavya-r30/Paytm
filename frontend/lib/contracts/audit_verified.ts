/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).
 */
export interface AuditVerified {
  event_id: string;
  type: "audit.verified";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: AuditVerification;
}
/**
 * This interface was referenced by `AuditVerified`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
export interface AuditVerification {
  valid: boolean;
  checked: number;
  bad_seq: number | null;
}
