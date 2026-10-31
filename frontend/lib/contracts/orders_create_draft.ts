/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface OrdersCreateDraft {
  channel: "whatsapp" | "storefront" | "device" | "preorder";
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  patron_id?: string;
  message_ref?: string;
  /**
   * @minItems 1
   * @maxItems 50
   */
  lines: [
    {
      item_id: string | null;
      text: string;
      qty_milli: number;
      confidence_bp: number;
    },
    ...{
      item_id: string | null;
      text: string;
      qty_milli: number;
      confidence_bp: number;
    }[]
  ];
}
