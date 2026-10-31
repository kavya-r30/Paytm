/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PublicStorefront {
  name: string;
  slug: string;
  hours: {
    start: string;
    end: string;
  };
  items: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    names: {
      [k: string]: string;
    };
    unit: string;
    price_paise: number;
    in_stock: boolean;
    category: string;
  }[];
  offers: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    program_id: string;
    terms: {
      amount_paise: number;
      min_spend_paise: number;
      expiry_days: number;
    };
    type: string;
  }[];
  invalidate_on: string[];
}
