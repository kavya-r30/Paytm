/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CapitalView {
  profile: {
    [k: string]: unknown;
  };
  need: {
    [k: string]: unknown;
  } | null;
  affordability: {
    [k: string]: unknown;
  };
  offers: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    lender: string;
    amount_paise: number;
    tenor_days: number;
    apr_bp: number;
    edi_paise: number;
    processing_fee_paise: number;
    total_repayment_paise: number;
    kfs_url: string;
    cooling_off_days: number;
    expires_at: string;
    affordable: boolean;
  }[];
  recommended_offer_id: string | null;
  console_pointer: {
    route: string;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    message_key: string;
  };
  invalidate_on: string[];
}
