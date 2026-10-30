/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ApprovalRequest {
  decision: "approve" | "snooze" | "edit" | "decline";
  edits?: {
    [k: string]: unknown;
  };
  decisions?: {
    [k: string]: "approve" | "snooze" | "decline";
  };
}
