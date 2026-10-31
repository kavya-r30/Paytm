/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PeersView {
  pack: string;
  status: "ready" | "insufficient_peers";
  n: number;
  metrics: {
    metric: string;
    p10: number;
    p25: number;
    p50: number;
    p75: number;
    p90: number;
  }[];
  invalidate_on: string[];
}
