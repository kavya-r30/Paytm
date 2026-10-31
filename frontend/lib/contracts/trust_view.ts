/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TrustView {
  tiers: {
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    commands: string[];
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    confirm_key: string;
  }[];
  roles: {
    role: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    max_tier: "R0" | "R1" | "R2" | "R3" | "R4";
    approve: ("R0" | "R1" | "R2" | "R3" | "R4")[];
  }[];
  activity: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    command_id: string;
    type: string;
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    status: string;
    actor_id: string | null;
    occurred_at: string;
  }[];
  audit: {
    ok: boolean;
    rows: number;
  };
  undo: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    command_id: string;
    type: string;
    until: string;
  }[];
  data_sharing: {
    peer_benchmarks: boolean;
  };
  data_requests: {
    kind: string;
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    patron_id: string;
    occurred_at: string;
  }[];
  invalidate_on: string[];
}
