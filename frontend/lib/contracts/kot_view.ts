/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface KotView {
  tickets: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    bill_id: string;
    token: number;
    status: "new" | "preparing" | "ready" | "served";
    age_seconds: number;
    items: {
      name: string;
      qty_milli: number;
      modifiers: string[];
    }[];
  }[];
  invalidate_on: string[];
}
