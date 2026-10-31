/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface HomeView {
  greeting: {
    owner_name: string;
    shop_name: string;
    now: string;
    part_of_day: "morning" | "midday" | "evening" | "night";
  };
  today: {
    sales_paise: number;
    bills: number;
    customers: number;
    new_customers: number;
    by_mode: {
      [k: string]: number;
    };
  };
  khata: {
    outstanding_paise: number;
    change_today_paise: number;
  };
  gates: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    gate_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    thread_id: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    type: string;
    status: string;
    expires_at: string;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    title_key: string;
    summary_params: {
      [k: string]: string | number | null;
    };
  }[];
  brief: {
    [k: string]: unknown;
  } | null;
  data_sufficiency: {
    status: "cold_start" | "learning" | "ready";
    days_of_history: number;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    reason_key: string;
  };
  invalidate_on: string[];
}
