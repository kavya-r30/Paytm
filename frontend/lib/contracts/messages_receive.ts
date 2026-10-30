/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface MessagesReceive {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  thread_ref: string;
  persona_ref: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  patron_id?: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  supplier_id?: string;
  kind: "text" | "voice_note" | "image" | "document" | "button";
  text: string;
}
