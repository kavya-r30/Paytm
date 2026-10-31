/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StockAdjust {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  item_id: string;
  batch_id?: string | null;
  delta_qty_milli: number;
  /**
   * A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).
   */
  reason: string;
}
