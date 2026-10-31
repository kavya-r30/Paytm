/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface OfferDetailView {
  program: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    type: string;
    status: string;
    funding: string;
    terms: {
      amount_paise: number;
      min_spend_paise: number;
      expiry_days: number;
    };
    budget_paise: number;
    spent_paise: number;
    liability: {
      issued_paise: number;
      redeemed_paise: number;
      expired_paise: number;
      outstanding_paise: number;
    };
    treated: number;
    holdout: number;
    issued: number;
    valid_until: string;
  };
  issuances: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    kind: string;
    amount_paise: number;
    state: string;
    funding: string;
    expires_at: string;
    patron_id: string | null;
  }[];
  invalidate_on: string[];
}
