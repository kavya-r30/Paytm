/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface GrowView {
  diagnostics: {
    current: {
      customers: number;
      visits: number;
      sales_paise: number;
    };
    previous: {
      customers: number;
      visits: number;
      sales_paise: number;
    };
    change_paise: number;
    parts: {
      customers_paise: number;
      frequency_paise: number;
      basket_paise: number;
    };
  };
  peers: {
    [k: string]: unknown;
  };
  levers: {
    name: string;
    enabled: boolean;
    eligible: number;
    estimate_paise: number;
    label: "estimate";
    gate: string;
  }[];
  plans: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    goal_key: string;
    status: string;
    budget_paise: number;
    levers: string[];
  }[];
  advisor: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    account_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    patron_id: string;
    current_limit_paise: number;
    suggested_limit_paise: number;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    reason_key: string;
  }[];
  invalidate_on: string[];
}
