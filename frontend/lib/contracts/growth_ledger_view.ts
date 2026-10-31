/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface GrowthLedgerView {
  entries: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    campaign_id: string;
    lever: string;
    treated_n: number;
    holdout_n: number;
    measured: {
      [k: string]: unknown;
    };
    direct_paise: number;
    reward_cost_paise: number;
    label: "measured" | "direct" | "estimated";
  }[];
  impact: {
    measured_paise: number;
    direct_paise: number;
    estimated_paise: number;
  };
  invalidate_on: string[];
}
