/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface GrowthCreatePlan {
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  goal_key: string;
  /**
   * @minItems 1
   * @maxItems 6
   */
  levers:
    | [string]
    | [string, string]
    | [string, string, string]
    | [string, string, string, string]
    | [string, string, string, string, string]
    | [string, string, string, string, string, string];
  budget_paise: number;
  holdout_bp: number;
}
