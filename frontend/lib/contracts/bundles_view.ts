/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface BundlesView {
  bundles: {
    items: string[];
    names: string[];
    price_paise: number;
    margin_bp: number;
    support: number;
  }[];
  preorders: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    patron_id: string;
    total_paise: number;
    deposit_paise: number;
    status: string;
  }[];
  invalidate_on: string[];
}
