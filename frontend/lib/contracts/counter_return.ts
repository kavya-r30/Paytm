/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CounterReturn {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  bill_id: string;
  /**
   * @minItems 1
   * @maxItems 50
   */
  lines: [
    {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      line_id: string;
      qty_milli: number;
    },
    ...{
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      line_id: string;
      qty_milli: number;
    }[]
  ];
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  reason_key: string;
  refund_mode: "cash" | "store_credit" | "upi" | "khata";
}
