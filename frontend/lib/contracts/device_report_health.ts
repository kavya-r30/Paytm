/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface DeviceReportHealth {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  device_id: string;
  connected: boolean;
  battery_pct: number;
  mic_muted: boolean;
  volume_pct: number;
  queue_size: number;
  last_sync_at?: string;
}
