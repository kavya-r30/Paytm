/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface OffersExcludePayers {
  /**
   * @minItems 1
   * @maxItems 50
   */
  payer_refs: [string, ...string[]];
}
