/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TreasuryRailsEvent {
  status: "pending" | "success" | "failed";
  utr: string;
  amount_paise: number;
  mode: "upi_qr" | "upi_static" | "upi_link";
  order_ref?: string;
  payer_ref?: string;
  payer_name?: string;
}
