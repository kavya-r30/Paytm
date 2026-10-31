/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface NotificationsView {
  needs_you: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    gate_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    thread_id: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    type: string;
    status: string;
    expires_at: string;
  }[];
  done: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    command_id: string;
    type: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    occurred_at: string;
    undo_until: string | null;
  }[];
  snoozed: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    gate_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    thread_id: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    type: string;
    status: string;
    expires_at: string;
  }[];
  invalidate_on: string[];
}
