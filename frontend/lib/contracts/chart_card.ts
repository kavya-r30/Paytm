/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ChartCard {
  type: "chart";
  chart_no: number;
  kind: string;
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  title_key: string;
  x: {
    [k: string]: unknown;
  };
  series: {
    [k: string]: unknown;
  }[];
  data: {
    [k: string]: unknown;
  }[];
  data_ref: string;
  as_of: string;
  takeaway: {
    [k: string]: unknown;
  };
  invalidate_on: string[];
}
