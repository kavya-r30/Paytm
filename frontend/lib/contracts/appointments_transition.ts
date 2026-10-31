/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface AppointmentsTransition {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  appointment_id: string;
  to: "checked_in" | "completed" | "no_show" | "cancelled";
}
