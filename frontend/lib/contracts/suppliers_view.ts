/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface SuppliersView {
  suppliers: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    name: string;
    lang: string;
    lead_days: number;
    open_pos: number;
    payable_paise: number;
  }[];
  invalidate_on: string[];
}
