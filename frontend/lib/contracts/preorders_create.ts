/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface PreordersCreate {
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  patron_id: string;
  /**
   * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
   */
  account_id: string;
  /**
   * @minItems 1
   * @maxItems 10
   */
  items:
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ]
    | [
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        },
        {
          /**
           * A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).
           */
          item_id: string;
          qty_milli: number;
        }
      ];
  deposit_paise: number;
}
