/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CounterCheckout {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  bill_id: string;
  /**
   * @minItems 1
   * @maxItems 4
   */
  payments:
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
        },
        {
          mode: "cash" | "card";
          amount_paise: number;
          tendered_paise?: number;
        }
      ];
  coupon_code?: string;
}
