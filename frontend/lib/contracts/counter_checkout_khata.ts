/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CounterCheckoutKhata {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  bill_id: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  account_id: string;
  khata_paise: number;
  /**
   * @minItems 0
   * @maxItems 3
   */
  payments:
    | []
    | [
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        }
      ]
    | [
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        },
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        }
      ]
    | [
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        },
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        },
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        }
      ];
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  member_id?: string;
  limit_override?: boolean;
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  reason_key?: string;
}
