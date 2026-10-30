/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface FeedbackView {
  average_bp: number | null;
  count: number;
  ratings: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    target_kind: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    target_id: string;
    rating: number;
    complaint_key: string | null;
    occurred_at: string;
  }[];
  complaints: number;
  invalidate_on: string[];
}
