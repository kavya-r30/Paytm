/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * RFC 9457 problem details with a stable code and an i18n message key (spec Part C1).
 */
export interface Problem {
  type: string;
  title: string;
  status: number;
  /**
   * A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).
   */
  code: string;
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  message_key: string;
  detail?: string;
  /**
   * Values interpolated into the message_key text.
   */
  params?: {
    /**
     * integer is listed before number so whole numbers (e.g. paise) stay integers through Pydantic.
     */
    [k: string]: string | number | boolean;
  };
}
