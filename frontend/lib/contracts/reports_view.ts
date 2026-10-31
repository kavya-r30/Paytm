/* Generated from contracts. Do not edit; run `python dev.py gen`. */

export interface ReportsView {
  month: string;
  profile: "unregistered" | "composition" | "regular";
  pnl: {
    month: string;
    sales_paise: number;
    returns_paise: number;
    cogs_paise: number;
    gross_profit_paise: number;
    expenses: {
      category: string;
      amount_paise: number;
    }[];
    expenses_paise: number;
    reward_cost_paise: number;
    net_paise: number;
  };
  gst: {
    month: string;
    invoices: number;
    rates: {
      rate_bp: number;
      taxable_paise: number;
      cgst_paise: number;
      sgst_paise: number;
      total_paise: number;
    }[];
    totals: {
      taxable_paise: number;
      cgst_paise: number;
      sgst_paise: number;
      total_paise: number;
    };
  };
  closed_months: {
    month: string;
    net_paise: number;
  }[];
  scheduled: {
    id: string;
    cadence: string;
  }[];
  invalidate_on: string[];
}
