/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PatronView {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  patron_id: string;
  display_name: string;
  lang: string;
  consent: {
    marketing: boolean;
    reminders: boolean;
    receipts: boolean;
  };
  household_members: {
    /**
     * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
     */
    id: string;
    display_name: string;
  }[];
  rewards: {
    stamps: number;
    available_rewards: number;
    available_value_paise: number;
  };
  invalidate_on: string[];
}
