/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TtsResult {
  text: string;
  spoken_text: string;
  lang: string;
  audio_b64: string | null;
  mode: "live" | "replay" | "unavailable";
  invalidate_on: string[];
}
