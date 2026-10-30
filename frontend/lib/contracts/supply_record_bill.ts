/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface SupplyRecordBill {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  po_id: string;
  bill_ref: string;
  /**
   * @minItems 1
   * @maxItems 100
   */
  lines: [
    {
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      item_id: string;
      qty_milli: number;
      unit_price_paise: number;
    },
    ...{
      /**
       * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
       */
      item_id: string;
      qty_milli: number;
      unit_price_paise: number;
    }[]
  ];
  due_on: string;
}
