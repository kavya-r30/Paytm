/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CounterAddLines {
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
      item_id: string;
      qty_milli?: number;
      amount_paise?: number;
      /**
       * @minItems 0
       * @maxItems 10
       */
      modifier_ids?:
        | []
        | [string]
        | [string, string]
        | [string, string, string]
        | [string, string, string, string]
        | [string, string, string, string, string]
        | [string, string, string, string, string, string]
        | [string, string, string, string, string, string, string]
        | [string, string, string, string, string, string, string, string]
        | [string, string, string, string, string, string, string, string, string]
        | [string, string, string, string, string, string, string, string, string, string];
      added_via: "scan" | "tap" | "voice" | "search" | "hint";
      unit_price_paise?: number;
      /**
       * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
       */
      reason_key?: string;
      rx_seen?: boolean;
    },
    ...{
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      item_id: string;
      qty_milli?: number;
      amount_paise?: number;
      /**
       * @minItems 0
       * @maxItems 10
       */
      modifier_ids?:
        | []
        | [string]
        | [string, string]
        | [string, string, string]
        | [string, string, string, string]
        | [string, string, string, string, string]
        | [string, string, string, string, string, string]
        | [string, string, string, string, string, string, string]
        | [string, string, string, string, string, string, string, string]
        | [string, string, string, string, string, string, string, string, string]
        | [string, string, string, string, string, string, string, string, string, string];
      added_via: "scan" | "tap" | "voice" | "search" | "hint";
      unit_price_paise?: number;
      /**
       * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
       */
      reason_key?: string;
      rx_seen?: boolean;
    }[]
  ];
}
