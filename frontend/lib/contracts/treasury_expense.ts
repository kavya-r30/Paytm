/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TreasuryExpense {
  category: "rent" | "salary" | "electricity" | "transport" | "supplies" | "repairs" | "other";
  amount_paise: number;
  paid_from: "cash" | "upi" | "bank";
  /**
   * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
   */
  note_key?: string;
}
