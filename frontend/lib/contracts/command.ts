/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface CommandRequest {
  /**
   * A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).
   */
  type: string;
  payload: {
    [k: string]: unknown;
  };
}
