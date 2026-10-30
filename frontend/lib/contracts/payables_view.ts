/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PayablesView {
  payables: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    supplier_ref: string;
    amount_paise: number;
    due_on: string;
    paid_paise: number;
    balance_paise: number;
  }[];
  invalidate_on: string[];
}
