/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CampaignView {
  campaign: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    plan_id: string;
    lever: string;
    status: string;
    stop_reason: string | null;
    treated: number;
    holdout: number;
    sent: number;
    result: {
      [k: string]: unknown;
    };
  };
  invalidate_on: string[];
}
