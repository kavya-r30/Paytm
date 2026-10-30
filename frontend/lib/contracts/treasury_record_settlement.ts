/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface TreasuryRecordSettlement {
  external_ref: string;
  date: string;
  gross_paise: number;
  net_paise: number;
  /**
   * @minItems 0
   * @maxItems 20
   */
  lines:
    | []
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ]
    | [
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        },
        {
          kind: "fee" | "edi" | "refund" | "other";
          amount_paise: number;
        }
      ];
  /**
   * @minItems 0
   * @maxItems 5000
   */
  utrs: string[];
}
