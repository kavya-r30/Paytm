/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface LedgerSendReminder {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  account_id: string;
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  template_key: string;
}
