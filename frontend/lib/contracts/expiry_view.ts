/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ExpiryView {
  batches: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    batch_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    days_to_expiry: number | null;
    recalled: boolean;
    qty_milli: number;
  }[];
  invalidate_on: string[];
}
