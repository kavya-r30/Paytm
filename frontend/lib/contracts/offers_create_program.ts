/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface OffersCreateProgram {
  type: "next_txn_cashback" | "instant_cashback" | "first_time_coupon" | "payment_count" | "item_coupon";
  rules: {
    reward_paise: number;
    min_spend_paise?: number;
    validity_days?: number;
    count?: number;
    combine_minutes?: number;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id?: string;
  };
  terms: {
    amount_paise: number;
    min_spend_paise: number;
    expiry_days: number;
  };
  budget_paise: number;
  daily_budget_paise?: number;
  funding: "merchant" | "platform";
  holdout_bp: number;
  include_regulars?: boolean;
  valid_from: string;
  valid_until: string;
}
