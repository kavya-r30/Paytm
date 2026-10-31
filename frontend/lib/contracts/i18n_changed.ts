/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).
 */
export interface LanguageChanged {
  event_id: string;
  type: "i18n.changed";
  merchant_id: string;
  occurred_at: string;
  actor: Actor;
  /**
   * Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick).
   */
  causation_id: string | null;
  payload: {
    screen_lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
    speech_lang: "hi-IN" | "en-IN" | "mr-IN" | "ta-IN" | "bn-IN" | "gu-IN" | "te-IN";
    customer_lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
  };
}
/**
 * This interface was referenced by `LanguageChanged`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  kind: "owner" | "staff" | "customer" | "supplier" | "agent" | "system" | "simulator";
  id?: string | null;
}
