/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface GrnView {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  po_id: string;
  received: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    qty_milli: number;
    batch_id: string | null;
  }[];
  billed: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    qty_milli: number;
    unit_price_paise: number;
  }[];
  variances: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    kind: "price" | "qty";
    expected: number;
    actual: number;
    delta_paise: number;
  }[];
  claim_id: string | null;
  invalidate_on: string[];
}
