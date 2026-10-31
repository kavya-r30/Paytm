/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TreasuryRefund {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  payment_id: string;
  amount_paise: number;
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  reason_key: string;
}
