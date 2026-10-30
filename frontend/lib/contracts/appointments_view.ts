/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface AppointmentsView {
  date: string;
  staff: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    name: string;
    skills: string[];
    appointments: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      id: string;
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      service_item_id: string;
      staff_id: string | null;
      patron_id: string | null;
      start_at: string | null;
      end_at: string | null;
      status: string;
      source: string;
    }[];
  }[];
  walk_ins: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    service_item_id: string;
    staff_id: string | null;
    patron_id: string | null;
    start_at: string | null;
    end_at: string | null;
    status: string;
    source: string;
  }[];
  no_shows: number;
  invalidate_on: string[];
}
