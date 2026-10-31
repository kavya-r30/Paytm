/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface AskView {
  session: string | null;
  turns: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    surface: string;
    heard: string;
    intent: string;
    said: string;
    created_at: string;
  }[];
  invalidate_on: string[];
}
