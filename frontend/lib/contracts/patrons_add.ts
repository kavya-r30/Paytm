/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PatronsAdd {
  display_name: string;
  /**
   * UI (screen) locale.
   */
  lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
  identities?: {
    kind: "vpa" | "phone" | "spoken_name" | "payer_name";
    value: string;
  }[];
}
