/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface HealthView {
  device: {
    [k: string]: unknown;
  } | null;
  offline_queue: {
    size: number;
    last_sync_at: string | null;
  };
  providers: {
    name: string;
    configured: boolean;
    mode: "live" | "fallback" | "replay" | "unknown";
  }[];
  ai_spend_today_paise: number;
  backup: {
    last_snapshot_at: string | null;
  };
  invalidate_on: string[];
}
