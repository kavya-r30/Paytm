/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ShiftView {
  current: {
    id: string;
    staff_id: string;
    opened_at: string;
    closed_at?: string | null;
    float_paise: number;
    expected_paise: number;
    counted_paise?: number | null;
    variance_paise?: number | null;
  } | null;
  invalidate_on: string[];
}
