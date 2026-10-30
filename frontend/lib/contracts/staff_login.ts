/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StaffLogin {
  device_credential: string;
  staff_id: string;
  pin: string;
  channel: "device" | "console";
}
