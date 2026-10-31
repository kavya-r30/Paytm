/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StaffAddCommand {
  name: string;
  role: "owner" | "manager" | "cashier" | "helper";
}
