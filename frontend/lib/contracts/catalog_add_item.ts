/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CatalogAddItem {
  sku: string;
  names: {
    [k: string]: string;
  };
  unit: string;
  mrp_paise: number;
  price_paise: number;
  cost_paise: number;
  category: string;
  aliases?: string[];
  barcodes?: string[];
  hsn?: string;
  gst_rate_bp?: number;
  details?: {
    salt?: string;
    strength?: string;
    form?: string;
    pack_size?: string;
    schedule?: string;
    rx_required?: boolean;
    duration_minutes?: number;
    required_skill?: string;
  };
  modifier_groups?: {
    name: string;
    required: boolean;
    /**
     * @minItems 1
     */
    options: [
      {
        name: string;
        delta_paise: number;
      },
      ...{
        name: string;
        delta_paise: number;
      }[]
    ];
  }[];
  recipe?: {
    item_id: string;
    qty_milli: number;
  }[];
}
