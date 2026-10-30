/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).
 */
export interface ApprovalRequested {
  event_id: string;
  type: "approval.requested";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: CommandResult;
}
/**
 * This interface was referenced by `ApprovalRequested`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
export interface CommandResult {
  scope?: {
    type: string;
    payload: {
      [k: string]: unknown;
    };
    conditions: {
      [k: string]: unknown;
    };
  };
  expires_at?: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  command_id: string;
  status: "executed" | "needs_approval" | "queued" | "snoozed";
  /**
   * Risk tier of a command (spec Part C6).
   */
  tier?: "R0" | "R1" | "R2" | "R3" | "R4";
  data?: {
    [k: string]: unknown;
  };
  envelope?: Envelope;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  gate_id?: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  thread_id?: string;
  due_at?: string;
}
/**
 * Everything Arth says or shows arrives as one envelope (spec Part C3).
 */
export interface Envelope {
  turn_id: string;
  lang: Lang;
  speech?: Speech | null;
  caption?: Caption | null;
  /**
   * Who may see a payload: a surface never renders content for an audience it does not serve.
   */
  audience: "all" | "owner" | "customer";
  cards: Card[];
  nav?: Nav | null;
  /**
   * v6: at most 3; UI shows 2–3 chips including screen defaults.
   *
   * @maxItems 3
   */
  followups: [] | [Followup] | [Followup, Followup] | [Followup, Followup, Followup];
  provenance: Provenance[];
  presence: Presence;
  led?: Led | null;
  tier?: ("R0" | "R1" | "R2" | "R3" | "R4") | null;
  undo?: Undo | null;
  sensitivity: "normal" | "discreet";
  fallback?: Fallback | null;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Lang".
 */
export interface Lang {
  /**
   * UI (screen) locale.
   */
  screen: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
  /**
   * Speech locale. Speech engines take language-REGION codes, so Hinglish (hi-Latn on screen) is spoken as hi-IN.
   */
  speech: "hi-IN" | "en-IN" | "mr-IN" | "ta-IN" | "bn-IN" | "gu-IN" | "te-IN";
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Speech".
 */
export interface Speech {
  text: string;
  voice?: string;
  ssml_ready?: boolean;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Caption".
 */
export interface Caption {
  heard?: string;
  said?: string;
}
/**
 * Base card. Each card type adds its own fields; per-type schemas arrive with the layer that produces them (see contracts/README.md).
 *
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Card".
 */
export interface Card {
  type:
    | "bill"
    | "hint"
    | "approval"
    | "batch"
    | "verdict"
    | "chart"
    | "forecast"
    | "brief"
    | "offer"
    | "plan"
    | "campaign"
    | "patron"
    | "stock"
    | "po"
    | "quote_compare"
    | "claim"
    | "memory"
    | "draft"
    | "capital"
    | "nudge"
    | "pipeline"
    | "receipt"
    | "health";
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  id?: string;
  /**
   * Who may see a payload: a surface never renders content for an audience it does not serve.
   */
  audience?: "all" | "owner" | "customer";
  /**
   * Arth's annotation; grounded before it is sent
   */
  note?: string;
  [k: string]: unknown;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Nav".
 */
export interface Nav {
  screen: string;
  params?: {
    [k: string]: string;
  };
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Followup".
 */
export interface Followup {
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  label_key: string;
  turn_text: string;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Provenance".
 */
export interface Provenance {
  kind: string;
  count?: number;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Presence".
 */
export interface Presence {
  state: "idle" | "listening" | "thinking" | "speaking" | "needs_you" | "done" | "alert";
  gaze?: string;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Led".
 */
export interface Led {
  pattern: string;
  color: string;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Undo".
 */
export interface Undo {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  command_id: string;
  until: string;
}
/**
 * This interface was referenced by `Envelope`'s JSON-Schema
 * via the `definition` "Fallback".
 */
export interface Fallback {
  channel: string;
  thread?: string;
}
