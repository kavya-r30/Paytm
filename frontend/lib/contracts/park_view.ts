/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ParkView {
  bills: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    patron_id: string | null;
    total_paise: number;
    lines: number;
    opened_at: string;
    patron_name: string | null;
  }[];
  invalidate_on: string[];
}
