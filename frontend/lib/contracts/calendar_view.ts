/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CalendarView {
  city: string;
  upcoming: {
    id: string;
    kind: string;
    name: string;
    start: string;
    end: string;
    days_until: number;
    confidence: string;
    source: string;
  }[];
  local_events: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    name: string;
    kind: string;
    start: string;
    end: string;
  }[];
  tentative_within_60_days: number;
  invalidate_on: string[];
}
