/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface StaffLoginCommand {
  staff_id: string;
  device_id: string;
  channel: "device" | "console";
}
