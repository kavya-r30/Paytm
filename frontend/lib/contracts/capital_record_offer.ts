/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CapitalRecordOffer {
  lender: string;
  amount_paise: number;
  tenor_days: number;
  apr_bp: number;
  edi_paise: number;
  processing_fee_paise: number;
  kfs_url: string;
  cooling_off_days: number;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  purpose_ref?: string;
  expires_at: string;
}
