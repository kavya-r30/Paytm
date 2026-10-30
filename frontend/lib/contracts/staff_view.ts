/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StaffView {
  staff: {
    id: string;
    name: string;
    role: "owner" | "manager" | "cashier" | "helper";
  }[];
  invalidate_on: string[];
}
