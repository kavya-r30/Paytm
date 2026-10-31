/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface LayerPendingView {
  screen: string;
  status: "needs_more_data" | "not_built_yet";
  layer: "L3" | "L4" | "L5" | "L6";
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  reason_key: string;
  items: {
    [k: string]: unknown;
  }[];
  invalidate_on: string[];
}
