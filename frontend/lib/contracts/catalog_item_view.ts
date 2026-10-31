/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CatalogItemView {
  invalidate_on?: string[];
  id: string;
  sku: string;
  names: {
    [k: string]: string;
  };
  unit: string;
  category?: string;
  mrp_paise?: number;
  price_paise: number;
  cost_paise?: number;
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
  frequency?: number;
  aliases?: string[];
  barcodes?: string[];
  hsn?: string;
  gst_rate_bp?: number;
  modifier_groups: {
    name: string;
    required: boolean;
    /**
     * @minItems 1
     */
    options: [
      {
        name: string;
        delta_paise: number;
        id: string;
      },
      ...{
        name: string;
        delta_paise: number;
        id: string;
      }[]
    ];
    id: string;
  }[];
  recipe: {
    item_id: string;
    qty_milli: number;
  }[];
}
