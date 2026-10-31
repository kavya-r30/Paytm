/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TreasuryResolveException {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  exception_id: string;
  resolution: "dismissed" | "refunded" | "matched";
}
