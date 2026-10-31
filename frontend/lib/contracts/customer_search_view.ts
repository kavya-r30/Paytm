/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CustomerSearchView {
  customers: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    patron_id: string;
    display_name: string;
    confidence: number;
  }[];
  needs_clarification: boolean;
  invalidate_on: string[];
  recent: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    patron_id: string;
    display_name: string;
    phone_masked: string | null;
    khata_balance_paise: number | null;
    reward_stamps: number;
  }[];
}
