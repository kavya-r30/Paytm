/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface Scenario {
  scenario: string;
  title: string;
  pack: "kirana" | "cafe" | "pharmacy" | "salon";
  world: {
    days?: number;
    seed?: number;
    size?: "micro" | "small" | "medium";
    patrons?: number;
    cold_start?: boolean;
  };
  locale?: {
    screen?: string;
    speech?: string;
  };
  edition?: "display" | "voice";
  cut?: {
    [k: string]: string[];
  };
  /**
   * @minItems 1
   */
  scenes: [
    {
      id: string;
      title: string;
      edition?: "display" | "voice";
      /**
       * @minItems 1
       */
      beats: [
        {
          id: string;
          who?: string;
          cue: string;
          input?: {
            say_for_me?: string;
            surface?: "device" | "console" | "whatsapp" | "voice";
            command?: {
              type: string;
              payload?: {
                [k: string]: unknown;
              };
              approve?: boolean;
              /**
               * Fixed Idempotency-Key, to replay a queued (offline) command; default is a fresh key per command.
               */
              key?: string;
            };
            approve_all?: boolean;
            persona_action?: {
              persona: string;
              action: "pay_qr" | "pay_static" | "message" | "stop" | "pay_pending" | "complete";
              bill?: string;
              text?: string;
              amount_paise?: number;
              outcome?: string;
              utr?: string;
            };
            clock?: {
              advance_minutes?: number;
              jump_days?: number;
            };
            fault?: {
              rails?: "duplicate" | "drop" | "delay" | "wrong_amount";
              providers_down?: boolean;
            };
            locale?: {
              screen?: string;
              speech?: string;
            };
            settle?: boolean;
            tick?: boolean;
            read?: string;
          }[];
          save?: {
            [k: string]: string;
          };
          expect_turn?: {
            intent?: string;
            speech_contains?: string;
            presence?: string;
            nav?: string;
            tier?: string;
          };
          expect?: {
            view?: string;
            path?: string;
            equals?: unknown;
            gte?: number;
            lte?: number;
            len?: number;
            contains?: unknown;
            absent?: boolean;
            invariants?: boolean;
            sim_thread?: string;
            outbound_template?: string;
            present?: boolean;
            result?: string;
          }[];
          within_ms?: number;
          focus?: {
            device_screen?: string;
            phone?: string;
            customer_display?: string;
            evidence?: string;
            table?: string;
            playbook?: string;
          };
        },
        ...{
          id: string;
          who?: string;
          cue: string;
          input?: {
            say_for_me?: string;
            surface?: "device" | "console" | "whatsapp" | "voice";
            command?: {
              type: string;
              payload?: {
                [k: string]: unknown;
              };
              approve?: boolean;
              /**
               * Fixed Idempotency-Key, to replay a queued (offline) command; default is a fresh key per command.
               */
              key?: string;
            };
            approve_all?: boolean;
            persona_action?: {
              persona: string;
              action: "pay_qr" | "pay_static" | "message" | "stop" | "pay_pending" | "complete";
              bill?: string;
              text?: string;
              amount_paise?: number;
              outcome?: string;
              utr?: string;
            };
            clock?: {
              advance_minutes?: number;
              jump_days?: number;
            };
            fault?: {
              rails?: "duplicate" | "drop" | "delay" | "wrong_amount";
              providers_down?: boolean;
            };
            locale?: {
              screen?: string;
              speech?: string;
            };
            settle?: boolean;
            tick?: boolean;
            read?: string;
          }[];
          save?: {
            [k: string]: string;
          };
          expect_turn?: {
            intent?: string;
            speech_contains?: string;
            presence?: string;
            nav?: string;
            tier?: string;
          };
          expect?: {
            view?: string;
            path?: string;
            equals?: unknown;
            gte?: number;
            lte?: number;
            len?: number;
            contains?: unknown;
            absent?: boolean;
            invariants?: boolean;
            sim_thread?: string;
            outbound_template?: string;
            present?: boolean;
            result?: string;
          }[];
          within_ms?: number;
          focus?: {
            device_screen?: string;
            phone?: string;
            customer_display?: string;
            evidence?: string;
            table?: string;
            playbook?: string;
          };
        }[]
      ];
    },
    ...{
      id: string;
      title: string;
      edition?: "display" | "voice";
      /**
       * @minItems 1
       */
      beats: [
        {
          id: string;
          who?: string;
          cue: string;
          input?: {
            say_for_me?: string;
            surface?: "device" | "console" | "whatsapp" | "voice";
            command?: {
              type: string;
              payload?: {
                [k: string]: unknown;
              };
              approve?: boolean;
              /**
               * Fixed Idempotency-Key, to replay a queued (offline) command; default is a fresh key per command.
               */
              key?: string;
            };
            approve_all?: boolean;
            persona_action?: {
              persona: string;
              action: "pay_qr" | "pay_static" | "message" | "stop" | "pay_pending" | "complete";
              bill?: string;
              text?: string;
              amount_paise?: number;
              outcome?: string;
              utr?: string;
            };
            clock?: {
              advance_minutes?: number;
              jump_days?: number;
            };
            fault?: {
              rails?: "duplicate" | "drop" | "delay" | "wrong_amount";
              providers_down?: boolean;
            };
            locale?: {
              screen?: string;
              speech?: string;
            };
            settle?: boolean;
            tick?: boolean;
            read?: string;
          }[];
          save?: {
            [k: string]: string;
          };
          expect_turn?: {
            intent?: string;
            speech_contains?: string;
            presence?: string;
            nav?: string;
            tier?: string;
          };
          expect?: {
            view?: string;
            path?: string;
            equals?: unknown;
            gte?: number;
            lte?: number;
            len?: number;
            contains?: unknown;
            absent?: boolean;
            invariants?: boolean;
            sim_thread?: string;
            outbound_template?: string;
            present?: boolean;
            result?: string;
          }[];
          within_ms?: number;
          focus?: {
            device_screen?: string;
            phone?: string;
            customer_display?: string;
            evidence?: string;
            table?: string;
            playbook?: string;
          };
        },
        ...{
          id: string;
          who?: string;
          cue: string;
          input?: {
            say_for_me?: string;
            surface?: "device" | "console" | "whatsapp" | "voice";
            command?: {
              type: string;
              payload?: {
                [k: string]: unknown;
              };
              approve?: boolean;
              /**
               * Fixed Idempotency-Key, to replay a queued (offline) command; default is a fresh key per command.
               */
              key?: string;
            };
            approve_all?: boolean;
            persona_action?: {
              persona: string;
              action: "pay_qr" | "pay_static" | "message" | "stop" | "pay_pending" | "complete";
              bill?: string;
              text?: string;
              amount_paise?: number;
              outcome?: string;
              utr?: string;
            };
            clock?: {
              advance_minutes?: number;
              jump_days?: number;
            };
            fault?: {
              rails?: "duplicate" | "drop" | "delay" | "wrong_amount";
              providers_down?: boolean;
            };
            locale?: {
              screen?: string;
              speech?: string;
            };
            settle?: boolean;
            tick?: boolean;
            read?: string;
          }[];
          save?: {
            [k: string]: string;
          };
          expect_turn?: {
            intent?: string;
            speech_contains?: string;
            presence?: string;
            nav?: string;
            tier?: string;
          };
          expect?: {
            view?: string;
            path?: string;
            equals?: unknown;
            gte?: number;
            lte?: number;
            len?: number;
            contains?: unknown;
            absent?: boolean;
            invariants?: boolean;
            sim_thread?: string;
            outbound_template?: string;
            present?: boolean;
            result?: string;
          }[];
          within_ms?: number;
          focus?: {
            device_screen?: string;
            phone?: string;
            customer_display?: string;
            evidence?: string;
            table?: string;
            playbook?: string;
          };
        }[]
      ];
    }[]
  ];
  invariants?: "default" | "none";
}
