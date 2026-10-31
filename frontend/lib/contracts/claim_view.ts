/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ClaimView {
  claim: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    po_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    supplier_id: string;
    amount_paise: number;
    status: string;
    lang: string;
    created_at: string;
  };
  variances: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    kind: "price" | "qty";
    expected: number;
    actual: number;
    delta_paise: number;
    name: string;
  }[];
  invalidate_on: string[];
  supplier_name: string;
}
