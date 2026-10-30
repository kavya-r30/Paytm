/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PoView {
  po: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    supplier_id: string;
    status: string;
    total_paise: number;
    due_on: string | null;
    created_at: string;
    lines: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      item_id: string;
      name: string;
      qty_milli: number;
      unit_price_paise: number;
      amount_paise: number;
      last_price_paise: number | null;
    }[];
    supplier_name: string;
  };
  price_history: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    unit_price_paise: number;
    source: string;
    occurred_at: string;
  }[];
  invalidate_on: string[];
}
