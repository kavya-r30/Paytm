/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface InsightsView {
  sufficiency: {
    feature: string;
    status: "ready" | "learning";
    days_of_history: number;
    days_needed: number;
    bills: number;
    bills_needed: number;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    reason_key: string;
  }[];
  alerts: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    key: string;
    kind: string;
    severity: string;
    params: {
      [k: string]: unknown;
    };
    raised_at: string;
  }[];
  actions: {
    proactive: {
      [k: string]: unknown;
    }[];
    queued: {
      [k: string]: unknown;
    }[];
    snoozed: string[];
  };
  lifecycle: {
    [k: string]: number;
  };
  demand_clusters: {
    label: string;
    count: number;
    demand_ids: string[];
  }[];
  invalidate_on: string[];
}
