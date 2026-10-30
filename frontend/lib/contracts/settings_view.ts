/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface SettingsView {
  screen_lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
  speech_lang: "hi-IN" | "en-IN" | "mr-IN" | "ta-IN" | "bn-IN" | "gu-IN" | "te-IN";
  customer_lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
  name: string;
  vpa?: string;
  address?: string;
  gstin?: string;
  tax_profile: "unregistered" | "composition" | "regular";
  hours?: {
    start: string;
    end: string;
  };
  quiet_hours?: {
    start: string;
    end: string;
  };
  pack: string;
  marketing_consent_default: false;
  receipts_consent_default: false;
  invalidate_on?: string[];
}
