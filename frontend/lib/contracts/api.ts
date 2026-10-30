/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface paths {
    "/v1/views/stock": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getStockView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/expiry": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getExpiryView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/customers/search": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getCustomerSearchView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/patron/{patron_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPatronView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/khata": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getKhataView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/khata/{patron_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getKhataAccountView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/statement/{account_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getLedgerStatementView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/promises": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPromisesView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/payables": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPayablesView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/patrons": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["patronsadd"];
        delete?: never;
        options?: never;
        head?: never;
        patch: operations["patronsupdate_profile"];
        trace?: never;
    };
    "/v1/staff/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["staffLogin"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/staff": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["addStaff"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/catalog/search": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["searchCatalog"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/catalog/resolve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resolveCatalog"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/settings/language": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["languageSettings"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/onboarding": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["onboardingView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/settings/staff": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["staffSettings"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/staff/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["staffLoginView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/shift": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["shiftView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/item/{item_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["itemView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/commands": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["submitCommand"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/approvals/{thread_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["decideApproval"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/audit/verify": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["verifyAudit"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/healthz": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getHealth"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/stream": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Server-sent events. L0 streams spans; L1 adds domain events, envelopes and view invalidations. Requires a server-provisioned merchant session. Domain events and spans are merchant filtered. */
        get: operations["getStream"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/director/ping": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["directorPing"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        Problem: components["schemas"]["problem.schema"];
        Health: {
            /** @enum {string} */
            status: "ok";
            /** @enum {string} */
            mode: "dev" | "test" | "demo" | "prod";
            /** Format: date-time */
            clock: string;
            packs: string[];
            /** @description Whether each AI provider has an API key configured (booleans only, never the key) */
            providers: {
                [key: string]: boolean;
            };
        };
        Ok: {
            ok: boolean;
        };
        /** @description A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1). */
        PrefixedId: string;
        /** StockView */
        "stock_view.schema": {
            items: {
                item_id: components["schemas"]["PrefixedId"];
                on_hand_qty_milli: number;
                sellable_qty_milli: number;
                batches: {
                    id: components["schemas"]["PrefixedId"];
                    batch_no: string;
                    expires_on: string | null;
                    mrp_paise: number;
                    cost_paise: number;
                    recalled: boolean;
                    qty_milli: number;
                }[];
            }[];
            invalidate_on: string[];
        };
        NonEmptyString: string;
        /** @description A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours). */
        DottedCode: string;
        /** @description An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya. */
        MessageKey: string;
        /**
         * Problem
         * @description RFC 9457 problem details with a stable code and an i18n message key (spec Part C1).
         */
        "problem.schema": {
            /** Format: uri-reference */
            type: string;
            title: components["schemas"]["NonEmptyString"];
            status: number;
            code: components["schemas"]["DottedCode"];
            message_key: components["schemas"]["MessageKey"];
            detail?: string;
            /** @description Values interpolated into the message_key text. */
            params?: {
                [key: string]: string | number | boolean;
            };
        };
        /** ExpiryView */
        "expiry_view.schema": {
            batches: {
                batch_id: components["schemas"]["PrefixedId"];
                item_id: components["schemas"]["PrefixedId"];
                days_to_expiry: number | null;
                recalled: boolean;
                qty_milli: number;
            }[];
            invalidate_on: string[];
        };
        /** CustomerSearchView */
        "customer_search_view.schema": {
            customers: {
                patron_id: components["schemas"]["PrefixedId"];
                display_name: string;
                confidence: number;
            }[];
            needs_clarification: boolean;
            invalidate_on: string[];
        };
        /** PatronView */
        "patron_view.schema": {
            patron_id: components["schemas"]["PrefixedId"];
            display_name: string;
            lang: string;
            consent: {
                marketing: boolean;
                reminders: boolean;
                receipts: boolean;
            };
            household_members: {
                id: components["schemas"]["PrefixedId"];
                display_name: string;
            }[];
            rewards: {
                stamps: number;
                available_rewards: number;
                available_value_paise: number;
            };
            invalidate_on: string[];
        };
        /** KhataAccountView */
        "khata_account_view.schema": {
            account_id: components["schemas"]["PrefixedId"];
            /** Format: date-time */
            as_of: string;
            entries: {
                id: components["schemas"]["PrefixedId"];
                account_id: components["schemas"]["PrefixedId"];
                amount_paise: number;
                source: string;
                ref_id: components["schemas"]["PrefixedId"] | null;
                member_id: components["schemas"]["PrefixedId"] | null;
                reversal_of: components["schemas"]["PrefixedId"] | null;
                /** Format: date-time */
                occurred_at: string;
                /** @enum {unknown} */
                status: "open" | "disputed" | "acknowledged" | "resolved";
                allocated_paise: number;
                lines: {
                    item_id: components["schemas"]["PrefixedId"] | null;
                    description_key: string | null;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                }[];
            }[];
            payments: {
                payment_ref: components["schemas"]["PrefixedId"];
                amount_paise: number;
                mode: string;
                /** Format: date-time */
                occurred_at: string;
            }[];
            entries_paise: number;
            allocated_paise: number;
            balance_paise: number;
            advance_paise: number;
            invalidate_on: string[];
            patron_id: components["schemas"]["PrefixedId"];
            display_name: string;
            limit_paise: number;
            promises: {
                id: components["schemas"]["PrefixedId"];
                amount_paise: number;
                /** Format: date */
                due_on: string;
                /** Format: date-time */
                occurred_at: string;
                /** @enum {string} */
                status: "active" | "kept" | "broken";
            }[];
            pay_link_ref: components["schemas"]["PrefixedId"] | null;
        };
        /** KhataView */
        "khata_view.schema": {
            accounts: components["schemas"]["khata_account_view.schema"][];
            balance_paise: number;
            advance_paise: number;
            invalidate_on: string[];
        };
        /** LedgerStatementView */
        "ledger_statement_view.schema": {
            account_id: components["schemas"]["PrefixedId"];
            /** Format: date-time */
            as_of: string;
            entries: {
                id: components["schemas"]["PrefixedId"];
                account_id: components["schemas"]["PrefixedId"];
                amount_paise: number;
                source: string;
                ref_id: components["schemas"]["PrefixedId"] | null;
                member_id: components["schemas"]["PrefixedId"] | null;
                reversal_of: components["schemas"]["PrefixedId"] | null;
                /** Format: date-time */
                occurred_at: string;
                /** @enum {unknown} */
                status: "open" | "disputed" | "acknowledged" | "resolved";
                allocated_paise: number;
                lines: {
                    item_id: components["schemas"]["PrefixedId"] | null;
                    description_key: string | null;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                }[];
            }[];
            payments: {
                payment_ref: components["schemas"]["PrefixedId"];
                amount_paise: number;
                mode: string;
                /** Format: date-time */
                occurred_at: string;
            }[];
            entries_paise: number;
            allocated_paise: number;
            balance_paise: number;
            advance_paise: number;
            invalidate_on: string[];
            pay_link_ref: components["schemas"]["PrefixedId"] | null;
        };
        /** PromisesView */
        "promises_view.schema": {
            promises: {
                id: components["schemas"]["PrefixedId"];
                account_id: components["schemas"]["PrefixedId"];
                amount_paise: number;
                /** Format: date */
                due_on: string;
                /** @enum {unknown} */
                status: "active" | "kept" | "broken";
            }[];
            invalidate_on: string[];
        };
        /** PayablesView */
        "payables_view.schema": {
            payables: {
                id: components["schemas"]["PrefixedId"];
                supplier_ref: components["schemas"]["PrefixedId"];
                amount_paise: number;
                /** Format: date */
                due_on: string;
                paid_paise: number;
                balance_paise: number;
            }[];
            invalidate_on: string[];
        };
        /**
         * @description UI (screen) locale.
         * @enum {string}
         */
        Locale: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
        /** PatronsAdd */
        "patrons_add.schema": {
            display_name: string;
            lang: components["schemas"]["Locale"];
            identities?: {
                /** @enum {unknown} */
                kind: "vpa" | "phone" | "spoken_name" | "payer_name";
                value: string;
            }[];
        };
        /**
         * @description Risk tier of a command (spec Part C6).
         * @enum {string}
         */
        Tier: "R0" | "R1" | "R2" | "R3" | "R4";
        /**
         * @description Speech locale. Speech engines take language-REGION codes, so Hinglish (hi-Latn on screen) is spoken as hi-IN.
         * @enum {string}
         */
        SpeechLocale: "hi-IN" | "en-IN" | "mr-IN" | "ta-IN" | "bn-IN" | "gu-IN" | "te-IN";
        /**
         * @description Who may see a payload: a surface never renders content for an audience it does not serve.
         * @enum {string}
         */
        Audience: "all" | "owner" | "customer";
        Lang: {
            screen: components["schemas"]["Locale"];
            speech: components["schemas"]["SpeechLocale"];
        };
        Speech: {
            text: components["schemas"]["NonEmptyString"];
            voice?: string;
            ssml_ready?: boolean;
        };
        Caption: {
            heard?: string;
            said?: string;
        };
        /** @description Base card. Each card type adds its own fields; per-type schemas arrive with the layer that produces them (see contracts/README.md). */
        Card: {
            /** @enum {string} */
            type: "bill" | "hint" | "approval" | "batch" | "verdict" | "chart" | "forecast" | "brief" | "offer" | "plan" | "campaign" | "patron" | "stock" | "po" | "quote_compare" | "claim" | "memory" | "draft" | "capital" | "nudge" | "pipeline" | "receipt" | "health";
            id?: components["schemas"]["PrefixedId"];
            audience?: components["schemas"]["Audience"];
            /** @description Arth's annotation; grounded before it is sent */
            note?: string;
        } & {
            [key: string]: unknown;
        };
        Nav: {
            screen: components["schemas"]["NonEmptyString"];
            params?: {
                [key: string]: string;
            };
        };
        Followup: {
            label_key: components["schemas"]["MessageKey"];
            turn_text: components["schemas"]["NonEmptyString"];
        };
        Provenance: {
            kind: components["schemas"]["NonEmptyString"];
            count?: number;
        };
        Presence: {
            /** @enum {string} */
            state: "idle" | "listening" | "thinking" | "speaking" | "needs_you" | "done" | "alert";
            gaze?: string;
        };
        Led: {
            pattern: string;
            color: string;
        };
        Undo: {
            command_id: components["schemas"]["PrefixedId"];
            /** Format: date-time */
            until: string;
        };
        Fallback: {
            channel: string;
            thread?: string;
        };
        /**
         * Envelope
         * @description Everything Arth says or shows arrives as one envelope (spec Part C3).
         */
        "envelope.schema": {
            turn_id: string;
            lang: components["schemas"]["Lang"];
            speech?: components["schemas"]["Speech"] | null;
            caption?: components["schemas"]["Caption"] | null;
            audience: components["schemas"]["Audience"];
            cards: components["schemas"]["Card"][];
            nav?: components["schemas"]["Nav"] | null;
            /** @description v6: at most 3; UI shows 2–3 chips including screen defaults. */
            followups: components["schemas"]["Followup"][];
            provenance: components["schemas"]["Provenance"][];
            presence: components["schemas"]["Presence"];
            led?: components["schemas"]["Led"] | null;
            tier?: components["schemas"]["Tier"] | null;
            undo?: components["schemas"]["Undo"] | null;
            /** @enum {string} */
            sensitivity: "normal" | "discreet";
            fallback?: components["schemas"]["Fallback"] | null;
        };
        /** CommandResult */
        "command_result.schema": {
            scope?: {
                type: string;
                payload: Record<string, never>;
                conditions: Record<string, never>;
            };
            /** Format: date-time */
            expires_at?: string;
            command_id: components["schemas"]["PrefixedId"];
            /** @enum {unknown} */
            status: "executed" | "needs_approval" | "queued" | "snoozed";
            tier?: components["schemas"]["Tier"];
            data?: Record<string, never>;
            envelope?: components["schemas"]["envelope.schema"];
            gate_id?: components["schemas"]["PrefixedId"];
            thread_id?: components["schemas"]["PrefixedId"];
            /** Format: date-time */
            due_at?: string;
        };
        /** PatronsUpdateProfile */
        "patrons_update_profile.schema": {
            patron_id: components["schemas"]["PrefixedId"];
            display_name?: string;
            lang?: components["schemas"]["Locale"];
        };
        /** StaffLogin */
        "staff_login.schema": {
            device_credential: string;
            staff_id: string;
            pin: string;
            /** @enum {unknown} */
            channel: "device" | "console";
        };
        /** SessionResult */
        "session_result.schema": {
            token: string;
            staff_id: string;
            /** Format: date-time */
            expires_at: string;
        };
        /** StaffAdd */
        "staff_add.schema": {
            name: string;
            /** @enum {unknown} */
            role: "owner" | "manager" | "cashier" | "helper";
            pin: string;
        };
        /** CatalogSearchView */
        "catalog_search_view.schema": {
            items: {
                id: string;
                sku: string;
                names: {
                    [key: string]: string;
                };
                unit?: string;
                category?: string;
                mrp_paise?: number;
                price_paise: number;
                cost_paise?: number;
                details?: {
                    salt?: string;
                    strength?: string;
                    form?: string;
                    pack_size?: string;
                    schedule?: string;
                    rx_required?: boolean;
                    duration_minutes?: number;
                    required_skill?: string;
                };
                frequency?: number;
            }[];
            invalidate_on: string[];
        };
        /** ResolutionView */
        "resolution_view.schema": {
            /** @enum {unknown} */
            stage: "none" | "normalize" | "alias" | "transliteration" | "fuzzy" | "embedding";
            candidates: {
                id: string;
                sku: string;
                names: {
                    [key: string]: string;
                };
                unit: string;
                category?: string;
                mrp_paise?: number;
                price_paise: number;
                cost_paise?: number;
                details?: {
                    salt?: string;
                    strength?: string;
                    form?: string;
                    pack_size?: string;
                    schedule?: string;
                    rx_required?: boolean;
                    duration_minutes?: number;
                    required_skill?: string;
                };
                frequency: number;
                confidence?: number;
            }[];
            selected: {
                id: string;
                sku: string;
                names: {
                    [key: string]: string;
                };
                unit: string;
                category?: string;
                mrp_paise?: number;
                price_paise: number;
                cost_paise?: number;
                details?: {
                    salt?: string;
                    strength?: string;
                    form?: string;
                    pack_size?: string;
                    schedule?: string;
                    rx_required?: boolean;
                    duration_minutes?: number;
                    required_skill?: string;
                };
                frequency: number;
                confidence?: number;
            } | null;
            needs_clarification: boolean;
            invalidate_on: string[];
        };
        /** SettingsView */
        "settings_view.schema": {
            /** @enum {unknown} */
            screen_lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
            /** @enum {unknown} */
            speech_lang: "hi-IN" | "en-IN" | "mr-IN" | "ta-IN" | "bn-IN" | "gu-IN" | "te-IN";
            /** @enum {unknown} */
            customer_lang: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
            name: string;
            vpa?: string;
            address?: string;
            gstin?: string;
            /** @enum {unknown} */
            tax_profile: "unregistered" | "composition" | "regular";
            hours?: {
                start: string;
                end: string;
            };
            quiet_hours?: {
                start: string;
                end: string;
            };
            pack: string;
            /** @constant */
            marketing_consent_default: false;
            /** @constant */
            receipts_consent_default: false;
            invalidate_on?: string[];
        };
        /** OnboardingView */
        "onboarding_view.schema": {
            steps: string[];
            completed: string[];
            next_step: string | null;
            invalidate_on: string[];
        };
        /** StaffView */
        "staff_view.schema": {
            staff: {
                id: string;
                name: string;
                /** @enum {unknown} */
                role: "owner" | "manager" | "cashier" | "helper";
            }[];
            invalidate_on: string[];
        };
        /** ShiftView */
        "shift_view.schema": {
            current: {
                id: string;
                staff_id: string;
                opened_at: string;
                closed_at?: string | null;
                float_paise: number;
                expected_paise: number;
                counted_paise?: number | null;
                variance_paise?: number | null;
            } | null;
            invalidate_on: string[];
        };
        /** CatalogItemView */
        "catalog_item_view.schema": {
            invalidate_on?: string[];
            id: string;
            sku: string;
            names: {
                [key: string]: string;
            };
            unit: string;
            category?: string;
            mrp_paise?: number;
            price_paise: number;
            cost_paise?: number;
            details?: {
                salt?: string;
                strength?: string;
                form?: string;
                pack_size?: string;
                schedule?: string;
                rx_required?: boolean;
                duration_minutes?: number;
                required_skill?: string;
            };
            frequency?: number;
            aliases?: string[];
            barcodes?: string[];
            hsn?: string;
            gst_rate_bp?: number;
            modifier_groups: {
                name: string;
                required: boolean;
                options: {
                    name: string;
                    delta_paise: number;
                    id: string;
                }[];
                id: string;
            }[];
            recipe: {
                item_id: string;
                qty_milli: number;
            }[];
        };
        /** CommandRequest */
        "command.schema": {
            type: components["schemas"]["DottedCode"];
            payload: Record<string, never>;
        };
        /** ApprovalRequest */
        "approval.schema": {
            /** @enum {unknown} */
            decision: "approve" | "snooze" | "edit";
            edits?: Record<string, never>;
            decisions?: {
                [key: string]: "approve" | "snooze";
            };
        };
        /** AuditVerification */
        "audit_verification.schema": {
            valid: boolean;
            checked: number;
            bad_seq: number | null;
        };
    };
    responses: {
        /** @description RFC 9457 problem details (spec Part C1) */
        Problem: {
            headers: {
                [name: string]: unknown;
            };
            content: {
                "application/problem+json": components["schemas"]["problem.schema"];
            };
        };
    };
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    getStockView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["stock_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getExpiryView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["expiry_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getCustomerSearchView: {
        parameters: {
            query: {
                q: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["customer_search_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPatronView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                patron_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["patron_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getKhataView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["khata_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getKhataAccountView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                patron_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["khata_account_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getLedgerStatementView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                account_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ledger_statement_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPromisesView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["promises_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPayablesView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Scoped merchant read model */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["payables_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    patronsadd: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["patrons_add.schema"];
            };
        };
        responses: {
            /** @description PII-safe command result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["command_result.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    patronsupdate_profile: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["patrons_update_profile.schema"];
            };
        };
        responses: {
            /** @description PII-safe command result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["command_result.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    staffLogin: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["staff_login.schema"];
            };
        };
        responses: {
            /** @description staffLogin result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["session_result.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    addStaff: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["staff_add.schema"];
            };
        };
        responses: {
            /** @description addStaff result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["command_result.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    searchCatalog: {
        parameters: {
            query: {
                q: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description searchCatalog result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["catalog_search_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    resolveCatalog: {
        parameters: {
            query: {
                q: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description resolveCatalog result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["resolution_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    languageSettings: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description languageSettings result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["settings_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    onboardingView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description onboardingView result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["onboarding_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    staffSettings: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description staffSettings result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["staff_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    staffLoginView: {
        parameters: {
            query?: never;
            header: {
                "X-Device-Credential": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description staffLoginView result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["staff_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    shiftView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description shiftView result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["shift_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    itemView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                item_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description itemView result */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["catalog_item_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    submitCommand: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["command.schema"];
            };
        };
        responses: {
            /** @description Stored command result or approval gate */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["command_result.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    decideApproval: {
        parameters: {
            query?: never;
            header: {
                "Idempotency-Key": string;
            };
            path: {
                thread_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["approval.schema"];
            };
        };
        responses: {
            /** @description Decision results, one per gate for a batch */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["command_result.schema"] | {
                        items: components["schemas"]["command_result.schema"][];
                    };
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    verifyAudit: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Merchant audit integrity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["audit_verification.schema"];
                };
            };
            401: components["responses"]["Problem"];
        };
    };
    getHealth: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Service health */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Health"];
                };
            };
        };
    };
    getStream: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description SSE stream */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "text/event-stream": string;
                };
            };
            401: components["responses"]["Problem"];
        };
    };
    directorPing: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Director token accepted */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Ok"];
                };
            };
            401: components["responses"]["Problem"];
        };
    };
}
