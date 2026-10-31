/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface SupplyAddSupplier {
  name: string;
  phone?: string;
  /**
   * UI (screen) locale.
   */
  lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
  lead_days: number;
}
