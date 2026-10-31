/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface SupplyRecordQuote {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  supplier_id: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  item_id: string;
  unit_price_paise: number;
  valid_until?: string;
}
