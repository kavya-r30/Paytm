/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StockView {
  items: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    on_hand_qty_milli: number;
    sellable_qty_milli: number;
    batches: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      id: string;
      batch_no: string;
      expires_on: string | null;
      mrp_paise: number;
      cost_paise: number;
      recalled: boolean;
      qty_milli: number;
    }[];
    name: string;
    unit: string;
    category: string;
    target_qty_milli: number;
    status: "ok" | "low" | "out" | "untracked";
    supplier_name: string | null;
  }[];
  invalidate_on: string[];
}
