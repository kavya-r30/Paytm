/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StaffAdd {
  name: string;
  role: "owner" | "manager" | "cashier" | "helper";
  pin: string;
}
