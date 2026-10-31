/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface RunView {
  run: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    playbook: string;
    agent: string;
    subject: string;
    status: string;
    step: string;
    created_at: string;
    updated_at: string;
    context: {
      [k: string]: unknown;
    };
    wait: {
      [k: string]: unknown;
    } | null;
  };
  steps: {
    step: string;
    status: string;
    detail: {
      [k: string]: unknown;
    };
    occurred_at: string;
  }[];
  invalidate_on: string[];
}
