/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface OrderView {
  order: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    status: string;
    channel: string;
    patron_id: string | null;
    total_paise: number;
    created_at: string;
    lines: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      id: string;
      item_id: string | null;
      text: string;
      qty_milli: number;
      unit_price_paise: number;
      amount_paise: number;
      check: boolean;
    }[];
  };
  history: {
    from_state: string | null;
    to_state: string;
    actor_id: string;
    occurred_at: string;
  }[];
  pick_list: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    name: string;
    qty_milli: number;
  }[];
  allowed: string[];
  invalidate_on: string[];
}
