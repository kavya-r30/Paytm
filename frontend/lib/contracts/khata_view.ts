/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface KhataView {
  accounts: KhataAccountView[];
  balance_paise: number;
  advance_paise: number;
  invalidate_on: string[];
}
export interface KhataAccountView {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  account_id: string;
  as_of: string;
  entries: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    account_id: string;
    amount_paise: number;
    source: string;
    ref_id: string | null;
    member_id: string | null;
    reversal_of: string | null;
    occurred_at: string;
    status: "open" | "disputed" | "acknowledged" | "resolved";
    allocated_paise: number;
    lines: {
      item_id: string | null;
      description_key: string | null;
      qty_milli: number;
      unit_price_paise: number;
      amount_paise: number;
    }[];
  }[];
  payments: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    payment_ref: string;
    amount_paise: number;
    mode: string;
    occurred_at: string;
  }[];
  entries_paise: number;
  allocated_paise: number;
  balance_paise: number;
  advance_paise: number;
  invalidate_on: string[];
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  patron_id: string;
  display_name: string;
  limit_paise: number;
  promises: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    amount_paise: number;
    due_on: string;
    occurred_at: string;
    status: "active" | "kept" | "broken";
  }[];
  pay_link_ref: string | null;
}
