/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TurnRequest {
  text?: string;
  audio_b64?: string;
  surface: "device" | "console" | "whatsapp" | "voice";
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  bill_id?: string;
  /**
   * UI (screen) locale.
   */
  lang?: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
}
