/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface HisaabView {
  date: string;
  close: {
    [k: string]: unknown;
  } | null;
  today: {
    sales_paise: number;
    by_mode: {
      [k: string]: number;
    };
    expenses_paise: number;
    refunds_paise: number;
    khata_given_paise: number;
  };
  unmatched: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    payment_id: string;
    amount_paise: number;
    received_at: string;
    khata_patron_id: string | null;
    suggestions: {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      bill_id: string;
      total_paise: number;
      score_bp: number;
    }[];
  }[];
  exceptions: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    kind: string;
    payment_id: string | null;
    bill_id: string | null;
    status: string;
    opened_at: string;
  }[];
  settlements: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    date: string;
    gross_paise: number;
    net_paise: number;
    deductions: {
      kind: string;
      amount_paise: number;
    }[];
    explained: boolean;
  }[];
  shifts: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    staff_id: string;
    opened_at: string;
    closed_at: string | null;
    float_paise: number;
    expected_paise: number;
    counted_paise: number | null;
    variance_paise: number | null;
  }[];
  expenses: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    category: string;
    amount_paise: number;
    paid_from: string;
    occurred_at: string;
  }[];
  invalidate_on: string[];
}
