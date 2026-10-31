/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface GateView {
  gate: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    gate_id: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    thread_id: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    type: string;
    status: string;
    expires_at: string;
    scope: {
      [k: string]: unknown;
    };
    conditions: {
      [k: string]: unknown;
    };
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    title_key: string;
    summary_params: {
      [k: string]: string | number | null;
    };
  };
  readback_key: string | null;
  invalidate_on: string[];
}
