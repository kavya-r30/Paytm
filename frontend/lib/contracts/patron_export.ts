/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PatronExport {
  patron: {
    [k: string]: unknown;
  };
  identities: {
    kind: string;
    value: string;
  }[];
  consents: {
    purpose: string;
    granted: boolean;
    occurred_at: string;
  }[];
  khata: {
    [k: string]: unknown;
  } | null;
  bills: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    total_paise: number;
    closed_at: string | null;
  }[];
  invalidate_on: string[];
}
