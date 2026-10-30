/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface BillView {
  bill: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    status: "open" | "parked" | "closed" | "voided";
    patron_id: string | null;
    staff_id: string;
    opened_at: string;
    closed_at: string | null;
    total_paise: number;
    paid_paise: number;
    khata_paise: number;
    due_paise: number;
    lines: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      id: string;
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      item_id: string;
      name: string;
      qty_milli: number;
      unit_price_paise: number;
      amount_paise: number;
      added_via: string;
      modifier_ids: string[];
      price_override: boolean;
      batch_id: string | null;
    }[];
    payments: {
      mode: string;
      amount_paise: number;
      change_paise: number | null;
      ref_id: string | null;
    }[];
    ticket: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      id: string;
      token: number;
      status: "new" | "preparing" | "ready" | "served";
    } | null;
    upi: {
      order_ref: string;
      amount_paise: number;
      status: "waiting" | "pending" | "paid" | "failed" | "expired";
      expires_at: string;
    } | null;
    patron: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      id: string;
      display_name: string;
      lang: string;
      khata_balance_paise: number | null;
      reward_stamps: number;
    } | null;
  };
  parked_count: number;
  invalidate_on: string[];
  quick_items: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    name: string;
    price_paise: number;
    unit: string;
    category: string;
  }[];
  categories: {
    key: string;
    label: string;
  }[];
}
