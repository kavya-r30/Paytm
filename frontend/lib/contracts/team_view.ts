/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TeamView {
  helpers: {
    id: string;
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    name_key: string;
    agents: string[];
    status: "idle" | "working" | "waiting" | "paused";
    /**
     * Risk tier of a command (spec Part C6).
     */
    tier: "R0" | "R1" | "R2" | "R3" | "R4";
    pending_gates: number;
    open_work: number;
    line: string | null;
  }[];
  runs: {
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
  }[];
  work: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    kind: string;
    agent: string;
    title_key: string;
    params: {
      [k: string]: unknown;
    };
    urgency: number;
    status: string;
    created_at: string;
  }[];
  kill_switch: boolean;
  summary: {
    done_since_night: number;
    waiting_for_you: number;
  };
  invalidate_on: string[];
}
