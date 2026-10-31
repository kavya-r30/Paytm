/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CatalogBulkPrice {
  /**
   * @minItems 1
   * @maxItems 500
   */
  prices: [
    {
      item_id: string;
      price_paise: number;
    },
    ...{
      item_id: string;
      price_paise: number;
    }[]
  ];
}
