/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface OrdersView {
  orders: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    status: string;
    channel: string;
    patron_id: string | null;
    total_paise: number;
    created_at: string;
    lines: number;
    patron_name: string | null;
  }[];
  by_status: {
    [k: string]: number;
  };
  invalidate_on: string[];
}
