/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface DemandView {
  unmet: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    text: string;
    item_id: string | null;
    occurred_at: string;
  }[];
  clusters: {
    label: string;
    count: number;
  }[];
  status: "needs_more_data" | "ready";
  invalidate_on: string[];
}
