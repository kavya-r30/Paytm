/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CalendarAddLocalEvent {
  name: string;
  kind: "fair" | "market_day" | "local_festival" | "closure" | "other";
  start: string;
  end: string;
}
