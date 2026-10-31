/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ForecastView {
  metric: "sales" | "items";
  status: "ready" | "needs_more_data";
  actuals: {
    date: string;
    sales_paise: number;
  }[];
  days: {
    date: string;
    p10_paise: number;
    p50_paise: number;
    p90_paise: number;
    festive: boolean;
  }[];
  accuracy: {
    wape_bp: number | null;
    coverage_bp: number | null;
    window_days: number;
    within_band: number;
  };
  drivers: {
    /**
     * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
     */
    key: string;
    contribution_paise: number;
  }[];
  items: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    item_id: string;
    name: string;
    daily_qty_milli: number;
    horizon_qty_milli: number;
  }[];
  invalidate_on: string[];
}
