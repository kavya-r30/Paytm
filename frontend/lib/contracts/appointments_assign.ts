/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface AppointmentsAssign {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  appointment_id: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  staff_id: string;
  start_at: string;
}
