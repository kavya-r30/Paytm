/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface VerdictView {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  check_id: string;
  verdict: "received" | "not_received" | "pending" | "unclear";
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  headline_key: string;
  evidence: {
    kind: string;
    claimed: string | null;
    ledger: string | null;
    state: "match" | "mismatch" | "missing";
  }[];
  signals: {
    kind: string;
    state: string;
  }[];
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  footnote_key: string;
  invalidate_on: string[];
}
