/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PromisesView {
  promises: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    account_id: string;
    amount_paise: number;
    due_on: string;
    status: "active" | "kept" | "broken";
  }[];
  invalidate_on: string[];
}
