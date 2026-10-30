/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface LedgerAddEntry {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  account_id: string;
  amount_paise: number;
  /**
   * @minItems 1
   */
  lines: [
    {
      item_id: string | null;
      qty_milli: number;
      unit_price_paise: number;
      /**
       * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
       */
      description_key?: string;
    },
    ...{
      item_id: string | null;
      qty_milli: number;
      unit_price_paise: number;
      /**
       * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
       */
      description_key?: string;
    }[]
  ];
  source: "counter" | "voice" | "order" | "import";
  ref_id?: string | null;
  occurred_at?: string;
  member_id?: string | null;
  limit_override?: boolean;
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  reason_key?: string;
}
