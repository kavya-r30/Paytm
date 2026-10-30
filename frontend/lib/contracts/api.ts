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
    "/v1/views/home": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getHomeView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/notifications": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getNotificationsView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/gates/{gate_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGateView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/bill/{bill_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getBillView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/bill/{bill_id}/pay": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getBillPayView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/bill/{bill_id}/paid": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getBillPaidView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/park": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getParkView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/orders": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getOrdersView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/orders/{order_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getOrderView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/stock/expiry": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getStockExpiryView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/suppliers": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getSuppliersView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/po/{po_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPoView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/grn/{po_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGrnView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/claims/{claim_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getClaimView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/grow": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGrowView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/grow/plans/{plan_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGrowPlanView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/grow/demand": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGrowDemandView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/grow/bundles": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGrowBundlesView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/grow/ledger": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getGrowLedgerView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/campaigns/{campaign_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getCampaignView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/offers": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getOffersView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/offers/{program_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getOfferView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/storefront": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getStorefrontView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/team": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getTeamView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/runs/{run_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getRunView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/memory": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getMemoryView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/hisaab": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getHisaabView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getReportsView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/feedback": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getFeedbackView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/trust": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getTrustView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getHealthView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/capital": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getCapitalView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/kot": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getKotView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/appointments": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getAppointmentsView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/rx": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getRxView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/verdict/{check_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getVerdictView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/privacy/patrons/{patron_id}/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPatronExport"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/public/storefront/{slug}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPublicStorefront"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/webhooks/rails": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["railsWebhook"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/webhooks/messages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["messagesWebhook"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/rails/qr": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simRailsQr"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/pay/{token}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["simPayPage"];
        put?: never;
        post: operations["simPay"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/rails/static-pay": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simStaticPay"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/rails/complete": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simCompletePayment"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/rails/faults": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simRailsFaults"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/rails/settle": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simSettle"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/messages/threads": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["simThreads"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/messages/inbound": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simInbound"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/lender/offers": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simLenderOffers"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/tools/screenshot": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["simScreenshot"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/sim/personas": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["simPersonas"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/director/clock": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["directorClock"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/director/world": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["directorWorld"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/peers/{pack}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getPeers"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/calendar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getCalendarView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/director/session": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["directorSession"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/forecast": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getForecastView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/insights": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getInsightsView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analytics/{tool}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getAnalytics"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/charts/{number}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getChart"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/books/export/{kind}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getBooksExport"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/views/ask": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getAskView"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/turns": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["postTurn"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/tts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["getTts"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/work/batches": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["postWorkBatch"];
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
                name: string;
                unit: string;
                category: string;
                target_qty_milli: number;
                /** @enum {unknown} */
                status: "ok" | "low" | "out" | "untracked";
                supplier_name: string | null;
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
                name: string;
                batch_no: string;
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
            recent: {
                patron_id: components["schemas"]["PrefixedId"];
                display_name: string;
                phone_masked: string | null;
                khata_balance_paise: number | null;
                reward_stamps: number;
            }[];
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
         * @description Risk tier of a command (spec Part C6).
         * @enum {string}
         */
        Tier: "R0" | "R1" | "R2" | "R3" | "R4";
        /** HomeView */
        "home_view.schema": {
            greeting: {
                owner_name: string;
                shop_name: string;
                /** Format: date-time */
                now: string;
                /** @enum {unknown} */
                part_of_day: "morning" | "midday" | "evening" | "night";
            };
            today: {
                sales_paise: number;
                bills: number;
                customers: number;
                new_customers: number;
                by_mode: {
                    [key: string]: number;
                };
            };
            khata: {
                outstanding_paise: number;
                change_today_paise: number;
            };
            gates: {
                gate_id: components["schemas"]["PrefixedId"];
                thread_id: components["schemas"]["PrefixedId"];
                tier: components["schemas"]["Tier"];
                type: string;
                status: string;
                /** Format: date-time */
                expires_at: string;
                title_key: components["schemas"]["MessageKey"];
                summary_params: {
                    [key: string]: string | number | null;
                };
            }[];
            brief: Record<string, never> | null;
            data_sufficiency: {
                /** @enum {unknown} */
                status: "cold_start" | "learning" | "ready";
                days_of_history: number;
                reason_key: components["schemas"]["MessageKey"];
            };
            invalidate_on: string[];
        };
        /** NotificationsView */
        "notifications_view.schema": {
            needs_you: {
                gate_id: components["schemas"]["PrefixedId"];
                thread_id: components["schemas"]["PrefixedId"];
                tier: components["schemas"]["Tier"];
                type: string;
                status: string;
                /** Format: date-time */
                expires_at: string;
                title_key: components["schemas"]["MessageKey"];
                summary_params: {
                    [key: string]: string | number | null;
                };
            }[];
            done: {
                command_id: components["schemas"]["PrefixedId"];
                type: string;
                tier: components["schemas"]["Tier"];
                /** Format: date-time */
                occurred_at: string;
                undo_until: string | null;
            }[];
            snoozed: {
                gate_id: components["schemas"]["PrefixedId"];
                thread_id: components["schemas"]["PrefixedId"];
                tier: components["schemas"]["Tier"];
                type: string;
                status: string;
                /** Format: date-time */
                expires_at: string;
                title_key: components["schemas"]["MessageKey"];
                summary_params: {
                    [key: string]: string | number | null;
                };
            }[];
            invalidate_on: string[];
        };
        /** GateView */
        "gate_view.schema": {
            gate: {
                gate_id: components["schemas"]["PrefixedId"];
                thread_id: components["schemas"]["PrefixedId"];
                tier: components["schemas"]["Tier"];
                type: string;
                status: string;
                /** Format: date-time */
                expires_at: string;
                scope: Record<string, never>;
                conditions: Record<string, never>;
                title_key: components["schemas"]["MessageKey"];
                summary_params: {
                    [key: string]: string | number | null;
                };
            };
            readback_key: components["schemas"]["MessageKey"] | null;
            invalidate_on: string[];
        };
        /** BillView */
        "bill_view.schema": {
            bill: {
                id: components["schemas"]["PrefixedId"];
                /** @enum {unknown} */
                status: "open" | "parked" | "closed" | "voided";
                patron_id: components["schemas"]["PrefixedId"] | null;
                staff_id: string;
                /** Format: date-time */
                opened_at: string;
                closed_at: string | null;
                total_paise: number;
                paid_paise: number;
                khata_paise: number;
                due_paise: number;
                lines: {
                    id: components["schemas"]["PrefixedId"];
                    item_id: components["schemas"]["PrefixedId"];
                    name: string;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                    added_via: string;
                    modifier_ids: components["schemas"]["PrefixedId"][];
                    price_override: boolean;
                    batch_id: components["schemas"]["PrefixedId"] | null;
                }[];
                payments: {
                    mode: string;
                    amount_paise: number;
                    change_paise: number | null;
                    ref_id: string | null;
                }[];
                ticket: {
                    id: components["schemas"]["PrefixedId"];
                    token: number;
                    /** @enum {unknown} */
                    status: "new" | "preparing" | "ready" | "served";
                } | null;
                upi: {
                    order_ref: string;
                    amount_paise: number;
                    /** @enum {unknown} */
                    status: "waiting" | "pending" | "paid" | "failed" | "expired";
                    /** Format: date-time */
                    expires_at: string;
                } | null;
                patron: {
                    id: components["schemas"]["PrefixedId"];
                    display_name: string;
                    lang: string;
                    khata_balance_paise: number | null;
                    reward_stamps: number;
                } | null;
            };
            parked_count: number;
            invalidate_on: string[];
            quick_items: {
                item_id: components["schemas"]["PrefixedId"];
                name: string;
                price_paise: number;
                unit: string;
                category: string;
            }[];
            categories: {
                key: string;
                label: string;
            }[];
        };
        /** BillPayView */
        "bill_pay_view.schema": {
            bill: {
                id: components["schemas"]["PrefixedId"];
                /** @enum {unknown} */
                status: "open" | "parked" | "closed" | "voided";
                patron_id: components["schemas"]["PrefixedId"] | null;
                staff_id: string;
                /** Format: date-time */
                opened_at: string;
                closed_at: string | null;
                total_paise: number;
                paid_paise: number;
                khata_paise: number;
                due_paise: number;
                lines: {
                    id: components["schemas"]["PrefixedId"];
                    item_id: components["schemas"]["PrefixedId"];
                    name: string;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                    added_via: string;
                    modifier_ids: components["schemas"]["PrefixedId"][];
                    price_override: boolean;
                    batch_id: components["schemas"]["PrefixedId"] | null;
                }[];
                payments: {
                    mode: string;
                    amount_paise: number;
                    change_paise: number | null;
                    ref_id: string | null;
                }[];
                ticket: {
                    id: components["schemas"]["PrefixedId"];
                    token: number;
                    /** @enum {unknown} */
                    status: "new" | "preparing" | "ready" | "served";
                } | null;
                upi: {
                    order_ref: string;
                    amount_paise: number;
                    /** @enum {unknown} */
                    status: "waiting" | "pending" | "paid" | "failed" | "expired";
                    /** Format: date-time */
                    expires_at: string;
                } | null;
                patron: {
                    id: components["schemas"]["PrefixedId"];
                    display_name: string;
                    lang: string;
                    khata_balance_paise: number | null;
                    reward_stamps: number;
                } | null;
            };
            payee_vpa: string | null;
            alternatives: ("cash" | "khata" | "regenerate")[];
            exception: string | null;
            invalidate_on: string[];
        };
        /** BillPaidView */
        "bill_paid_view.schema": {
            bill: {
                id: components["schemas"]["PrefixedId"];
                /** @enum {unknown} */
                status: "open" | "parked" | "closed" | "voided";
                patron_id: components["schemas"]["PrefixedId"] | null;
                staff_id: string;
                /** Format: date-time */
                opened_at: string;
                closed_at: string | null;
                total_paise: number;
                paid_paise: number;
                khata_paise: number;
                due_paise: number;
                lines: {
                    id: components["schemas"]["PrefixedId"];
                    item_id: components["schemas"]["PrefixedId"];
                    name: string;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                    added_via: string;
                    modifier_ids: components["schemas"]["PrefixedId"][];
                    price_override: boolean;
                    batch_id: components["schemas"]["PrefixedId"] | null;
                }[];
                payments: {
                    mode: string;
                    amount_paise: number;
                    change_paise: number | null;
                    ref_id: string | null;
                }[];
                ticket: {
                    id: components["schemas"]["PrefixedId"];
                    token: number;
                    /** @enum {unknown} */
                    status: "new" | "preparing" | "ready" | "served";
                } | null;
                upi: {
                    order_ref: string;
                    amount_paise: number;
                    /** @enum {unknown} */
                    status: "waiting" | "pending" | "paid" | "failed" | "expired";
                    /** Format: date-time */
                    expires_at: string;
                } | null;
                patron: {
                    id: components["schemas"]["PrefixedId"];
                    display_name: string;
                    lang: string;
                    khata_balance_paise: number | null;
                    reward_stamps: number;
                } | null;
            };
            invoice: Record<string, never> | null;
            receipt: {
                /** @enum {unknown} */
                status: "queued" | "no_consent" | "walk_in";
                lang: string | null;
            };
            offers: {
                issuance_id: components["schemas"]["PrefixedId"];
                kind: string;
                amount_paise: number;
                min_spend_paise: number;
                /** Format: date-time */
                expires_at: string;
                code: string | null;
            }[];
            utr_tail: string | null;
            invalidate_on: string[];
        };
        /** ParkView */
        "park_view.schema": {
            bills: {
                id: components["schemas"]["PrefixedId"];
                patron_id: components["schemas"]["PrefixedId"] | null;
                total_paise: number;
                lines: number;
                /** Format: date-time */
                opened_at: string;
                patron_name: string | null;
            }[];
            invalidate_on: string[];
        };
        /** OrdersView */
        "orders_view.schema": {
            orders: {
                id: components["schemas"]["PrefixedId"];
                status: string;
                channel: string;
                patron_id: components["schemas"]["PrefixedId"] | null;
                total_paise: number;
                /** Format: date-time */
                created_at: string;
                lines: number;
                patron_name: string | null;
            }[];
            by_status: {
                [key: string]: number;
            };
            invalidate_on: string[];
        };
        /** OrderView */
        "order_view.schema": {
            order: {
                id: components["schemas"]["PrefixedId"];
                status: string;
                channel: string;
                patron_id: components["schemas"]["PrefixedId"] | null;
                total_paise: number;
                /** Format: date-time */
                created_at: string;
                lines: {
                    id: components["schemas"]["PrefixedId"];
                    item_id: components["schemas"]["PrefixedId"] | null;
                    text: string;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                    check: boolean;
                }[];
                patron_name: string | null;
            };
            history: {
                from_state: string | null;
                to_state: string;
                actor_id: string;
                /** Format: date-time */
                occurred_at: string;
            }[];
            pick_list: {
                item_id: components["schemas"]["PrefixedId"];
                name: string;
                qty_milli: number;
            }[];
            allowed: string[];
            invalidate_on: string[];
        };
        /** SuppliersView */
        "suppliers_view.schema": {
            suppliers: {
                id: components["schemas"]["PrefixedId"];
                name: string;
                lang: string;
                lead_days: number;
                open_pos: number;
                payable_paise: number;
            }[];
            invalidate_on: string[];
        };
        /** PoView */
        "po_view.schema": {
            po: {
                id: components["schemas"]["PrefixedId"];
                supplier_id: components["schemas"]["PrefixedId"];
                status: string;
                total_paise: number;
                due_on: string | null;
                /** Format: date-time */
                created_at: string;
                lines: {
                    item_id: components["schemas"]["PrefixedId"];
                    name: string;
                    qty_milli: number;
                    unit_price_paise: number;
                    amount_paise: number;
                    last_price_paise: number | null;
                }[];
                supplier_name: string;
            };
            price_history: {
                item_id: components["schemas"]["PrefixedId"];
                unit_price_paise: number;
                source: string;
                /** Format: date-time */
                occurred_at: string;
            }[];
            invalidate_on: string[];
        };
        /** GrnView */
        "grn_view.schema": {
            po_id: components["schemas"]["PrefixedId"];
            received: {
                item_id: components["schemas"]["PrefixedId"];
                qty_milli: number;
                batch_id: components["schemas"]["PrefixedId"] | null;
            }[];
            billed: {
                item_id: components["schemas"]["PrefixedId"];
                qty_milli: number;
                unit_price_paise: number;
            }[];
            variances: {
                item_id: components["schemas"]["PrefixedId"];
                /** @enum {unknown} */
                kind: "price" | "qty";
                expected: number;
                actual: number;
                delta_paise: number;
                name: string;
            }[];
            claim_id: components["schemas"]["PrefixedId"] | null;
            invalidate_on: string[];
            supplier_name: string;
        };
        /** ClaimView */
        "claim_view.schema": {
            claim: {
                id: components["schemas"]["PrefixedId"];
                po_id: components["schemas"]["PrefixedId"];
                supplier_id: components["schemas"]["PrefixedId"];
                amount_paise: number;
                status: string;
                lang: string;
                /** Format: date-time */
                created_at: string;
            };
            variances: {
                item_id: components["schemas"]["PrefixedId"];
                /** @enum {unknown} */
                kind: "price" | "qty";
                expected: number;
                actual: number;
                delta_paise: number;
                name: string;
            }[];
            invalidate_on: string[];
            supplier_name: string;
        };
        /** LayerPendingView */
        "layer_pending_view.schema": {
            screen: string;
            /** @enum {unknown} */
            status: "needs_more_data" | "not_built_yet";
            /** @enum {unknown} */
            layer: "L3" | "L4" | "L5" | "L6";
            reason_key: components["schemas"]["MessageKey"];
            items: Record<string, never>[];
            invalidate_on: string[];
        };
        /** DemandView */
        "demand_view.schema": {
            unmet: {
                id: components["schemas"]["PrefixedId"];
                text: string;
                item_id: components["schemas"]["PrefixedId"] | null;
                /** Format: date-time */
                occurred_at: string;
            }[];
            clusters: {
                label: string;
                count: number;
            }[];
            /** @enum {unknown} */
            status: "needs_more_data" | "ready";
            invalidate_on: string[];
        };
        /** OffersView */
        "offers_view.schema": {
            programs: {
                id: components["schemas"]["PrefixedId"];
                type: string;
                status: string;
                funding: string;
                terms: {
                    amount_paise: number;
                    min_spend_paise: number;
                    expiry_days: number;
                };
                budget_paise: number;
                spent_paise: number;
                liability: {
                    issued_paise: number;
                    redeemed_paise: number;
                    expired_paise: number;
                    outstanding_paise: number;
                };
                treated: number;
                holdout: number;
                issued: number;
                /** Format: date-time */
                valid_until: string;
            }[];
            liability: {
                issued_paise: number;
                redeemed_paise: number;
                expired_paise: number;
                outstanding_paise: number;
            };
            invalidate_on: string[];
        };
        /** OfferDetailView */
        "offer_detail_view.schema": {
            program: {
                id: components["schemas"]["PrefixedId"];
                type: string;
                status: string;
                funding: string;
                terms: {
                    amount_paise: number;
                    min_spend_paise: number;
                    expiry_days: number;
                };
                budget_paise: number;
                spent_paise: number;
                liability: {
                    issued_paise: number;
                    redeemed_paise: number;
                    expired_paise: number;
                    outstanding_paise: number;
                };
                treated: number;
                holdout: number;
                issued: number;
                /** Format: date-time */
                valid_until: string;
            };
            issuances: {
                id: components["schemas"]["PrefixedId"];
                kind: string;
                amount_paise: number;
                state: string;
                funding: string;
                /** Format: date-time */
                expires_at: string;
                patron_id: components["schemas"]["PrefixedId"] | null;
            }[];
            invalidate_on: string[];
        };
        /** StorefrontView */
        "storefront_view.schema": {
            slug: string | null;
            published: boolean;
            show_offers: boolean;
            items: number;
            url: string | null;
            invalidate_on: string[];
        };
        /** TeamView */
        "team_view.schema": {
            helpers: {
                id: string;
                name_key: components["schemas"]["MessageKey"];
                agents: string[];
                /** @enum {unknown} */
                status: "idle" | "working" | "waiting" | "paused";
                tier: components["schemas"]["Tier"];
                pending_gates: number;
                open_work: number;
                line: string | null;
            }[];
            runs: {
                id: components["schemas"]["PrefixedId"];
                playbook: string;
                agent: string;
                subject: string;
                status: string;
                step: string;
                /** Format: date-time */
                created_at: string;
                /** Format: date-time */
                updated_at: string;
            }[];
            work: {
                id: components["schemas"]["PrefixedId"];
                kind: string;
                agent: string;
                title_key: string;
                params: Record<string, never>;
                urgency: number;
                status: string;
                /** Format: date-time */
                created_at: string;
            }[];
            kill_switch: boolean;
            summary: {
                done_since_night: number;
                waiting_for_you: number;
            };
            invalidate_on: string[];
        };
        /** RunView */
        "run_view.schema": {
            run: {
                id: components["schemas"]["PrefixedId"];
                playbook: string;
                agent: string;
                subject: string;
                status: string;
                step: string;
                /** Format: date-time */
                created_at: string;
                /** Format: date-time */
                updated_at: string;
                context: Record<string, never>;
                wait: Record<string, never> | null;
            };
            steps: {
                step: string;
                status: string;
                detail: Record<string, never>;
                /** Format: date-time */
                occurred_at: string;
            }[];
            invalidate_on: string[];
        };
        /** MemoryView */
        "memory_view.schema": {
            facts: {
                id: components["schemas"]["PrefixedId"];
                subject: string;
                predicate: string;
                value: string;
                evidence: string[];
                source: string;
                /** @enum {unknown} */
                status: "active" | "unverified" | "retracted" | "forgotten";
                /** Format: date-time */
                created_at: string;
            }[];
            invalidate_on: string[];
        };
        /** HisaabView */
        "hisaab_view.schema": {
            /** Format: date */
            date: string;
            close: Record<string, never> | null;
            today: {
                sales_paise: number;
                by_mode: {
                    [key: string]: number;
                };
                expenses_paise: number;
                refunds_paise: number;
                khata_given_paise: number;
            };
            unmatched: {
                payment_id: components["schemas"]["PrefixedId"];
                amount_paise: number;
                /** Format: date-time */
                received_at: string;
                khata_patron_id: components["schemas"]["PrefixedId"] | null;
                suggestions: {
                    bill_id: components["schemas"]["PrefixedId"];
                    total_paise: number;
                    score_bp: number;
                }[];
            }[];
            exceptions: {
                id: components["schemas"]["PrefixedId"];
                kind: string;
                payment_id: components["schemas"]["PrefixedId"] | null;
                bill_id: components["schemas"]["PrefixedId"] | null;
                status: string;
                /** Format: date-time */
                opened_at: string;
            }[];
            settlements: {
                id: components["schemas"]["PrefixedId"];
                /** Format: date */
                date: string;
                gross_paise: number;
                net_paise: number;
                deductions: {
                    kind: string;
                    amount_paise: number;
                }[];
                explained: boolean;
            }[];
            shifts: {
                id: components["schemas"]["PrefixedId"];
                staff_id: string;
                /** Format: date-time */
                opened_at: string;
                closed_at: string | null;
                float_paise: number;
                expected_paise: number;
                counted_paise: number | null;
                variance_paise: number | null;
            }[];
            expenses: {
                id: components["schemas"]["PrefixedId"];
                category: string;
                amount_paise: number;
                paid_from: string;
                /** Format: date-time */
                occurred_at: string;
            }[];
            invalidate_on: string[];
        };
        /** ReportsView */
        "reports_view.schema": {
            month: string;
            /** @enum {unknown} */
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
        };
        /** FeedbackView */
        "feedback_view.schema": {
            average_bp: number | null;
            count: number;
            ratings: {
                id: components["schemas"]["PrefixedId"];
                target_kind: string;
                target_id: components["schemas"]["PrefixedId"];
                rating: number;
                complaint_key: components["schemas"]["MessageKey"] | null;
                /** Format: date-time */
                occurred_at: string;
            }[];
            complaints: number;
            invalidate_on: string[];
        };
        /** TrustView */
        "trust_view.schema": {
            tiers: {
                tier: components["schemas"]["Tier"];
                commands: string[];
                confirm_key: components["schemas"]["MessageKey"];
            }[];
            roles: {
                role: string;
                max_tier: components["schemas"]["Tier"];
                approve: components["schemas"]["Tier"][];
            }[];
            activity: {
                command_id: components["schemas"]["PrefixedId"];
                type: string;
                tier: components["schemas"]["Tier"];
                status: string;
                actor_id: string | null;
                /** Format: date-time */
                occurred_at: string;
            }[];
            audit: {
                ok: boolean;
                rows: number;
            };
            undo: {
                command_id: components["schemas"]["PrefixedId"];
                type: string;
                /** Format: date-time */
                until: string;
            }[];
            data_sharing: {
                peer_benchmarks: boolean;
            };
            data_requests: {
                kind: string;
                patron_id: components["schemas"]["PrefixedId"];
                /** Format: date-time */
                occurred_at: string;
            }[];
            invalidate_on: string[];
        };
        /** HealthView */
        "health_view.schema": {
            device: Record<string, never> | null;
            offline_queue: {
                size: number;
                last_sync_at: string | null;
            };
            providers: {
                name: string;
                configured: boolean;
                /** @enum {unknown} */
                mode: "live" | "fallback" | "replay" | "unknown";
            }[];
            ai_spend_today_paise: number;
            backup: {
                last_snapshot_at: string | null;
            };
            invalidate_on: string[];
        };
        /** CapitalView */
        "capital_view.schema": {
            profile: Record<string, never>;
            need: Record<string, never> | null;
            affordability: Record<string, never>;
            offers: {
                id: components["schemas"]["PrefixedId"];
                lender: string;
                amount_paise: number;
                tenor_days: number;
                apr_bp: number;
                edi_paise: number;
                processing_fee_paise: number;
                total_repayment_paise: number;
                kfs_url: string;
                cooling_off_days: number;
                /** Format: date-time */
                expires_at: string;
                affordable: boolean;
            }[];
            recommended_offer_id: components["schemas"]["PrefixedId"] | null;
            console_pointer: {
                route: string;
                message_key: components["schemas"]["MessageKey"];
            };
            invalidate_on: string[];
        };
        /** KotView */
        "kot_view.schema": {
            tickets: {
                id: components["schemas"]["PrefixedId"];
                bill_id: components["schemas"]["PrefixedId"];
                token: number;
                /** @enum {unknown} */
                status: "new" | "preparing" | "ready" | "served";
                age_seconds: number;
                items: {
                    name: string;
                    qty_milli: number;
                    modifiers: string[];
                }[];
            }[];
            invalidate_on: string[];
        };
        /** AppointmentsView */
        "appointments_view.schema": {
            /** Format: date */
            date: string;
            staff: {
                id: components["schemas"]["PrefixedId"];
                name: string;
                skills: string[];
                appointments: {
                    id: components["schemas"]["PrefixedId"];
                    service_item_id: components["schemas"]["PrefixedId"];
                    staff_id: components["schemas"]["PrefixedId"] | null;
                    patron_id: components["schemas"]["PrefixedId"] | null;
                    start_at: string | null;
                    end_at: string | null;
                    status: string;
                    source: string;
                }[];
            }[];
            walk_ins: {
                id: components["schemas"]["PrefixedId"];
                service_item_id: components["schemas"]["PrefixedId"];
                staff_id: components["schemas"]["PrefixedId"] | null;
                patron_id: components["schemas"]["PrefixedId"] | null;
                start_at: string | null;
                end_at: string | null;
                status: string;
                source: string;
            }[];
            no_shows: number;
            invalidate_on: string[];
        };
        /** RxView */
        "rx_view.schema": {
            rx_sales: {
                bill_id: components["schemas"]["PrefixedId"];
                item_id: components["schemas"]["PrefixedId"];
                name: string;
                staff_id: string;
                /** Format: date-time */
                occurred_at: string;
            }[];
            refills_due: {
                patron_id: components["schemas"]["PrefixedId"];
                item_id: components["schemas"]["PrefixedId"];
                /** Format: date */
                due_on: string;
                patron_name: string;
                item_name: string;
            }[];
            recalls: {
                batch_id: components["schemas"]["PrefixedId"];
                item_id: components["schemas"]["PrefixedId"];
                buyer_ids: components["schemas"]["PrefixedId"][];
                item_name: string;
            }[];
            invalidate_on: string[];
        };
        /** VerdictView */
        "verdict_view.schema": {
            check_id: components["schemas"]["PrefixedId"];
            /** @enum {unknown} */
            verdict: "received" | "not_received" | "pending" | "unclear";
            headline_key: components["schemas"]["MessageKey"];
            evidence: {
                kind: string;
                claimed: string | null;
                ledger: string | null;
                /** @enum {unknown} */
                state: "match" | "mismatch" | "missing";
            }[];
            signals: {
                kind: string;
                state: string;
            }[];
            footnote_key: components["schemas"]["MessageKey"];
            invalidate_on: string[];
        };
        /** PatronExport */
        "patron_export.schema": {
            patron: Record<string, never>;
            identities: {
                kind: string;
                value: string;
            }[];
            consents: {
                purpose: string;
                granted: boolean;
                /** Format: date-time */
                occurred_at: string;
            }[];
            khata: Record<string, never> | null;
            bills: {
                id: components["schemas"]["PrefixedId"];
                total_paise: number;
                closed_at: string | null;
            }[];
            invalidate_on: string[];
        };
        /** PublicStorefront */
        "public_storefront.schema": {
            name: string;
            slug: string;
            hours: {
                start: string;
                end: string;
            };
            items: {
                item_id: components["schemas"]["PrefixedId"];
                names: {
                    [key: string]: string;
                };
                unit: string;
                price_paise: number;
                in_stock: boolean;
                category: string;
            }[];
            offers: {
                program_id: components["schemas"]["PrefixedId"];
                terms: {
                    amount_paise: number;
                    min_spend_paise: number;
                    expiry_days: number;
                };
                type: string;
            }[];
            invalidate_on: string[];
        };
        /** PeersView */
        "peers_view.schema": {
            pack: string;
            /** @enum {unknown} */
            status: "ready" | "insufficient_peers";
            n: number;
            metrics: {
                metric: string;
                p10: number;
                p25: number;
                p50: number;
                p75: number;
                p90: number;
            }[];
            invalidate_on: string[];
        };
        /** CalendarView */
        "calendar_view.schema": {
            city: string;
            upcoming: {
                id: string;
                kind: string;
                name: string;
                /** Format: date */
                start: string;
                /** Format: date */
                end: string;
                days_until: number;
                confidence: string;
                source: string;
            }[];
            local_events: {
                id: components["schemas"]["PrefixedId"];
                name: string;
                kind: string;
                /** Format: date */
                start: string;
                /** Format: date */
                end: string;
            }[];
            tentative_within_60_days: number;
            invalidate_on: string[];
        };
        /** SessionResult */
        "session_result.schema": {
            token: string;
            staff_id: string;
            /** Format: date-time */
            expires_at: string;
        };
        /** ForecastView */
        "forecast_view.schema": {
            /** @enum {unknown} */
            metric: "sales" | "items";
            /** @enum {unknown} */
            status: "ready" | "needs_more_data";
            actuals: {
                /** Format: date */
                date: string;
                sales_paise: number;
            }[];
            days: {
                /** Format: date */
                date: string;
                p10_paise: number;
                p50_paise: number;
                p90_paise: number;
                festive: boolean;
            }[];
            accuracy: {
                wape_bp: number | null;
                coverage_bp: number | null;
                window_days: number;
                within_band: number;
            };
            drivers: {
                key: components["schemas"]["MessageKey"];
                contribution_paise: number;
            }[];
            items: {
                item_id: components["schemas"]["PrefixedId"];
                name: string;
                daily_qty_milli: number;
                horizon_qty_milli: number;
            }[];
            invalidate_on: string[];
        };
        /** InsightsView */
        "insights_view.schema": {
            sufficiency: {
                feature: string;
                /** @enum {unknown} */
                status: "ready" | "learning";
                days_of_history: number;
                days_needed: number;
                bills: number;
                bills_needed: number;
                reason_key: components["schemas"]["MessageKey"];
            }[];
            alerts: {
                id: components["schemas"]["PrefixedId"];
                key: string;
                kind: string;
                severity: string;
                params: Record<string, never>;
                /** Format: date-time */
                raised_at: string;
            }[];
            actions: {
                proactive: Record<string, never>[];
                queued: Record<string, never>[];
                snoozed: string[];
            };
            lifecycle: {
                [key: string]: number;
            };
            demand_clusters: {
                label: string;
                count: number;
                demand_ids: components["schemas"]["PrefixedId"][];
            }[];
            invalidate_on: string[];
        };
        /** ChartCard */
        "chart_card.schema": {
            /** @enum {unknown} */
            type: "chart";
            chart_no: number;
            kind: string;
            title_key: components["schemas"]["MessageKey"];
            x: Record<string, never>;
            series: Record<string, never>[];
            data: Record<string, never>[];
            data_ref: string;
            /** Format: date-time */
            as_of: string;
            takeaway: Record<string, never>;
            invalidate_on: string[];
        };
        /** AskView */
        "ask_view.schema": {
            session: string | null;
            turns: {
                id: components["schemas"]["PrefixedId"];
                surface: string;
                heard: string;
                intent: string;
                said: string;
                /** Format: date-time */
                created_at: string;
            }[];
            invalidate_on: string[];
        };
        /**
         * @description UI (screen) locale.
         * @enum {string}
         */
        Locale: "hi" | "en" | "hi-Latn" | "mr" | "ta" | "bn" | "gu" | "te";
        /** TurnRequest */
        "turn_request.schema": {
            text?: string;
            audio_b64?: string;
            /** @enum {unknown} */
            surface: "device" | "console" | "whatsapp" | "voice";
            bill_id?: components["schemas"]["PrefixedId"];
            lang?: components["schemas"]["Locale"];
        };
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
        /** TtsResult */
        "tts_result.schema": {
            text: string;
            spoken_text: string;
            lang: string;
            audio_b64: string | null;
            /** @enum {unknown} */
            mode: "live" | "replay" | "unavailable";
            invalidate_on: string[];
        };
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
            decision: "approve" | "snooze" | "edit" | "decline";
            edits?: Record<string, never>;
            decisions?: {
                [key: string]: "approve" | "snooze" | "decline";
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
            query?: {
                q?: string;
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
    getHomeView: {
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
                    "application/json": components["schemas"]["home_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getNotificationsView: {
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
                    "application/json": components["schemas"]["notifications_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGateView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                gate_id: string;
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
                    "application/json": components["schemas"]["gate_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getBillView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                bill_id: string;
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
                    "application/json": components["schemas"]["bill_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getBillPayView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                bill_id: string;
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
                    "application/json": components["schemas"]["bill_pay_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getBillPaidView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                bill_id: string;
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
                    "application/json": components["schemas"]["bill_paid_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getParkView: {
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
                    "application/json": components["schemas"]["park_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getOrdersView: {
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
                    "application/json": components["schemas"]["orders_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getOrderView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                order_id: string;
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
                    "application/json": components["schemas"]["order_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getStockExpiryView: {
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
    getSuppliersView: {
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
                    "application/json": components["schemas"]["suppliers_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPoView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                po_id: string;
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
                    "application/json": components["schemas"]["po_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGrnView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                po_id: string;
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
                    "application/json": components["schemas"]["grn_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getClaimView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                claim_id: string;
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
                    "application/json": components["schemas"]["claim_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGrowView: {
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
                    "application/json": components["schemas"]["layer_pending_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGrowPlanView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                plan_id: string;
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
                    "application/json": components["schemas"]["layer_pending_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGrowDemandView: {
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
                    "application/json": components["schemas"]["demand_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGrowBundlesView: {
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
                    "application/json": components["schemas"]["layer_pending_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getGrowLedgerView: {
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
                    "application/json": components["schemas"]["layer_pending_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getCampaignView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                campaign_id: string;
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
                    "application/json": components["schemas"]["layer_pending_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getOffersView: {
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
                    "application/json": components["schemas"]["offers_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getOfferView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                program_id: string;
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
                    "application/json": components["schemas"]["offer_detail_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getStorefrontView: {
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
                    "application/json": components["schemas"]["storefront_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getTeamView: {
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
                    "application/json": components["schemas"]["team_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getRunView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
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
                    "application/json": components["schemas"]["run_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getMemoryView: {
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
                    "application/json": components["schemas"]["memory_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getHisaabView: {
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
                    "application/json": components["schemas"]["hisaab_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getReportsView: {
        parameters: {
            query?: {
                month?: string;
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
                    "application/json": components["schemas"]["reports_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getFeedbackView: {
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
                    "application/json": components["schemas"]["feedback_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getTrustView: {
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
                    "application/json": components["schemas"]["trust_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getHealthView: {
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
                    "application/json": components["schemas"]["health_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getCapitalView: {
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
                    "application/json": components["schemas"]["capital_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getKotView: {
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
                    "application/json": components["schemas"]["kot_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getAppointmentsView: {
        parameters: {
            query?: {
                date?: string;
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
                    "application/json": components["schemas"]["appointments_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getRxView: {
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
                    "application/json": components["schemas"]["rx_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getVerdictView: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                check_id: string;
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
                    "application/json": components["schemas"]["verdict_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPatronExport: {
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
                    "application/json": components["schemas"]["patron_export.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPublicStorefront: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                slug: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Public shop page (nothing personal) */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["public_storefront.schema"];
                };
            };
            404: components["responses"]["Problem"];
        };
    };
    railsWebhook: {
        parameters: {
            query?: never;
            header: {
                "x-sim-signature": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    messagesWebhook: {
        parameters: {
            query?: never;
            header: {
                "x-sim-signature": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simRailsQr: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simPayPage: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                token: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simPay: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                token: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simStaticPay: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simCompletePayment: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simRailsFaults: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simSettle: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simThreads: {
        parameters: {
            query: {
                merchant_id: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simInbound: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simLenderOffers: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simScreenshot: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    simPersonas: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    directorClock: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    directorWorld: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getPeers: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                pack: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["peers_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    getCalendarView: {
        parameters: {
            query?: {
                city?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["calendar_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            409: components["responses"]["Problem"];
        };
    };
    directorSession: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description A real staff session for a seeded shop (presenter only) */
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
    getForecastView: {
        parameters: {
            query?: {
                metric?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["forecast_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            404: components["responses"]["Problem"];
            422: components["responses"]["Problem"];
        };
    };
    getInsightsView: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["insights_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
            404: components["responses"]["Problem"];
            422: components["responses"]["Problem"];
        };
    };
    getAnalytics: {
        parameters: {
            query?: {
                start?: string;
                end?: string;
            };
            header?: never;
            path: {
                tool: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            404: components["responses"]["Problem"];
            422: components["responses"]["Problem"];
        };
    };
    getChart: {
        parameters: {
            query?: {
                format?: string;
            };
            header?: never;
            path: {
                number: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["chart_card.schema"];
                };
            };
            401: components["responses"]["Problem"];
            404: components["responses"]["Problem"];
            422: components["responses"]["Problem"];
        };
    };
    getBooksExport: {
        parameters: {
            query?: {
                month?: string;
            };
            header?: never;
            path: {
                kind: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            401: components["responses"]["Problem"];
            404: components["responses"]["Problem"];
            422: components["responses"]["Problem"];
        };
    };
    getAskView: {
        parameters: {
            query?: {
                session?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description The shared turn log (session memory) */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ask_view.schema"];
                };
            };
            401: components["responses"]["Problem"];
        };
    };
    postTurn: {
        parameters: {
            query?: never;
            header: {
                "idempotency-key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["turn_request.schema"];
            };
        };
        responses: {
            /** @description Response envelope v2 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["envelope.schema"];
                };
            };
            401: components["responses"]["Problem"];
            422: components["responses"]["Problem"];
            503: components["responses"]["Problem"];
        };
    };
    getTts: {
        parameters: {
            query: {
                text: string;
                lang?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Normalised spoken text and audio when a provider is reachable */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["tts_result.schema"];
                };
            };
            401: components["responses"]["Problem"];
        };
    };
    postWorkBatch: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": Record<string, never>;
            };
        };
        responses: {
            /** @description Thread id for one batched ask; answer it via POST /v1/approvals/{thread_id} */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
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
