/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * The newest record of a kind in the session's shop, so a detail screen opened without an id shows real data (null: the shop has none yet, the screen shows its empty state).
 */
export interface LatestRefView {
  kind:
    | "bill_open"
    | "bill_closed"
    | "gate"
    | "po"
    | "claim"
    | "offer"
    | "plan"
    | "campaign"
    | "run"
    | "order"
    | "verdict"
    | "item"
    | "patron";
  id: string | null;
  invalidate_on: string[];
}
