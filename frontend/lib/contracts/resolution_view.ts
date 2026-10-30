/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ResolutionView {
  stage: "none" | "normalize" | "alias" | "transliteration" | "fuzzy" | "embedding";
  /**
   * @maxItems 5
   */
  candidates:
    | []
    | [
        {
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
          frequency: number;
          confidence?: number;
        }
      ]
    | [
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        }
      ]
    | [
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        }
      ]
    | [
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        }
      ]
    | [
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        },
        {
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
          frequency: number;
          confidence?: number;
        }
      ];
  selected: {
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
    frequency: number;
    confidence?: number;
  } | null;
  needs_clarification: boolean;
  invalidate_on: string[];
}
