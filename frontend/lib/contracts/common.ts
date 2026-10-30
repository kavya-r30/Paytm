/* Generated from contracts. Do not edit; run `python dev.py gen`. */

/**
 * UI (screen) locale.
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "Locale".
 */
export type Locale = "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
/**
 * Speech locale. Speech engines take language-REGION codes, so Hinglish (hi-Latn on screen) is spoken as hi-IN.
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "SpeechLocale".
 */
export type SpeechLocale = "hi-IN" | "en-IN" | "mr-IN" | "ta-IN" | "bn-IN" | "gu-IN" | "te-IN";
/**
 * Who may see a payload: a surface never renders content for an audience it does not serve.
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "Audience".
 */
export type Audience = "all" | "owner" | "customer";
/**
 * Risk tier of a command (spec Part C6).
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "Tier".
 */
export type Tier = "R0" | "R1" | "R2" | "R3" | "R4";
/**
 * A bare ULID (Crockford base32, 26 characters).
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "Ulid".
 */
export type Ulid = string;
/**
 * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "PrefixedId".
 */
export type PrefixedId = string;
/**
 * A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "DottedCode".
 */
export type DottedCode = string;
/**
 * An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.
 *
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "MessageKey".
 */
export type MessageKey = string;
/**
 * This interface was referenced by `Common`'s JSON-Schema
 * via the `definition` "NonEmptyString".
 */
export type NonEmptyString = string;

/**
 * Shared definitions referenced by every other contract (spec Part C1). Reference them as `common.schema.json#/definitions/<Name>`.
 */
export interface Common {
  [k: string]: unknown;
}
