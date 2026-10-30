/* Generated from contracts. Do not edit; run `python dev.py gen`. */

import type { AppointmentsAssign } from './appointments_assign';
import type { AppointmentsBook } from './appointments_book';
import type { AppointmentsTransition } from './appointments_transition';
import type { AppointmentsView } from './appointments_view';
import type { AppointmentsWalkIn } from './appointments_walk_in';
import type { ApprovalRequest } from './approval';
import type { ApprovalDecided } from './approval_decided';
import type { ApprovalRequested } from './approval_requested';
import type { AuditVerification } from './audit_verification';
import type { AuditVerified } from './audit_verified';
import type { BatchRecalled } from './batch_recalled';
import type { BillChanged } from './bill_changed';
import type { BillPaid } from './bill_paid';
import type { BillPaidView } from './bill_paid_view';
import type { BillPayView } from './bill_pay_view';
import type { BillPriceOverride } from './bill_price_override';
import type { BillReturned } from './bill_returned';
import type { BillTicketChanged } from './bill_ticket_changed';
import type { BillView } from './bill_view';
import type { BooksCloseMonth } from './books_close_month';
import type { BooksMonthClosed } from './books_month_closed';
import type { CapitalApplied } from './capital_applied';
import type { CapitalApply } from './capital_apply';
import type { CapitalOfferReceived } from './capital_offer_received';
import type { CapitalRecordOffer } from './capital_record_offer';
import type { CapitalView } from './capital_view';
import type { CatalogAddItem } from './catalog_add_item';
import type { CatalogBulkPrice } from './catalog_bulk_price';
import type { CatalogChangePrice } from './catalog_change_price';
import type { CatalogImportItems } from './catalog_import_items';
import type { CatalogItemAdded } from './catalog_item_added';
import type { CatalogItemView } from './catalog_item_view';
import type { CatalogPriceChanged } from './catalog_price_changed';
import type { CatalogSearchView } from './catalog_search_view';
import type { ClaimView } from './claim_view';
import type { CommandRequest } from './command';
import type { CommandExecuted } from './command_executed';
import type { CommandResult } from './command_result';
import type { Common } from './common';
import type { ConsentGrant } from './consent_grant';
import type { ConsentStop } from './consent_stop';
import type { ConsentWithdraw } from './consent_withdraw';
import type { CounterAddLines } from './counter_add_lines';
import type { CounterAdvanceTicket } from './counter_advance_ticket';
import type { CounterAttachPatron } from './counter_attach_patron';
import type { CounterCheckout } from './counter_checkout';
import type { CounterCheckoutKhata } from './counter_checkout_khata';
import type { CounterOpenBill } from './counter_open_bill';
import type { CounterPark } from './counter_park';
import type { CounterRemoveLine } from './counter_remove_line';
import type { CounterRequestUpi } from './counter_request_upi';
import type { CounterResume } from './counter_resume';
import type { CounterReturn } from './counter_return';
import type { CounterSendToKitchen } from './counter_send_to_kitchen';
import type { CounterSetQty } from './counter_set_qty';
import type { CounterUndo } from './counter_undo';
import type { CounterVoidBill } from './counter_void_bill';
import type { CreditChanged } from './credit_changed';
import type { CreditPayableChanged } from './credit_payable_changed';
import type { CreditReceiptRequested } from './credit_receipt_requested';
import type { CreditReminderRequested } from './credit_reminder_requested';
import type { CreditStatementRequested } from './credit_statement_requested';
import type { CustomerSearchView } from './customer_search_view';
import type { DemandView } from './demand_view';
import type { DeviceHealthReported } from './device_health_reported';
import type { DeviceReportHealth } from './device_report_health';
import type { Envelope } from './envelope';
import type { DomainEvent } from './event';
import type { ExpiryView } from './expiry_view';
import type { FeedbackRecord } from './feedback_record';
import type { FeedbackRecorded } from './feedback_recorded';
import type { FeedbackView } from './feedback_view';
import type { GateView } from './gate_view';
import type { GrnView } from './grn_view';
import type { HealthView } from './health_view';
import type { HisaabView } from './hisaab_view';
import type { HomeView } from './home_view';
import type { LanguageChanged } from './i18n_changed';
import type { KhataAccountView } from './khata_account_view';
import type { KhataView } from './khata_view';
import type { KotView } from './kot_view';
import type { LayerPendingView } from './layer_pending_view';
import type { LedgerAcknowledgeEntry } from './ledger_acknowledge_entry';
import type { LedgerAddEntry } from './ledger_add_entry';
import type { LedgerAddPayable } from './ledger_add_payable';
import type { LedgerApplyAdvance } from './ledger_apply_advance';
import type { LedgerApplyVerifiedPayment } from './ledger_apply_verified_payment';
import type { LedgerDisputeEntry } from './ledger_dispute_entry';
import type { LedgerOpenAccount } from './ledger_open_account';
import type { LedgerPayPayable } from './ledger_pay_payable';
import type { LedgerRecordDeposit } from './ledger_record_deposit';
import type { LedgerRecordPayment } from './ledger_record_payment';
import type { LedgerRecordPromise } from './ledger_record_promise';
import type { LedgerResolveDispute } from './ledger_resolve_dispute';
import type { LedgerReverseEntry } from './ledger_reverse_entry';
import type { LedgerSendReminder } from './ledger_send_reminder';
import type { LedgerSendStatement } from './ledger_send_statement';
import type { LedgerSetLimit } from './ledger_set_limit';
import type { LedgerStatementView } from './ledger_statement_view';
import type { MerchantBootstrap } from './merchant_bootstrap';
import type { MerchantUpdateSettings } from './merchant_update_settings';
import type { NotificationsView } from './notifications_view';
import type { OfferCashbackRequested } from './offer_cashback_requested';
import type { OfferClawedBack } from './offer_clawed_back';
import type { OfferDetailView } from './offer_detail_view';
import type { OfferExpired } from './offer_expired';
import type { OfferIssued } from './offer_issued';
import type { OfferProgramChanged } from './offer_program_changed';
import type { OfferRedeemed } from './offer_redeemed';
import type { OffersCreateProgram } from './offers_create_program';
import type { OffersExcludePayers } from './offers_exclude_payers';
import type { OffersExpireDue } from './offers_expire_due';
import type { OffersPauseProgram } from './offers_pause_program';
import type { OffersView } from './offers_view';
import type { OnboardingCompleteStep } from './onboarding_complete_step';
import type { OnboardingStarted } from './onboarding_started';
import type { OnboardingUpdated } from './onboarding_updated';
import type { OnboardingView } from './onboarding_view';
import type { OrderAppointmentChanged } from './order_appointment_changed';
import type { OrderChanged } from './order_changed';
import type { OrderView } from './order_view';
import type { OrdersAccept } from './orders_accept';
import type { OrdersAdvance } from './orders_advance';
import type { OrdersCreateDraft } from './orders_create_draft';
import type { OrdersDecline } from './orders_decline';
import type { OrdersPlace } from './orders_place';
import type { OrdersSettle } from './orders_settle';
import type { OrdersSubstitute } from './orders_substitute';
import type { OrdersView } from './orders_view';
import type { ParkView } from './park_view';
import type { PatronChanged } from './patron_changed';
import type { PatronConsentChanged } from './patron_consent_changed';
import type { PatronExport } from './patron_export';
import type { PatronMerged } from './patron_merged';
import type { PatronRewardChanged } from './patron_reward_changed';
import type { PatronView } from './patron_view';
import type { PatronsAdd } from './patrons_add';
import type { PatronsAddCommand } from './patrons_add_command';
import type { PatronsAddHouseholdMember } from './patrons_add_household_member';
import type { PatronsMerge } from './patrons_merge';
import type { PatronsProposeMerge } from './patrons_propose_merge';
import type { PatronsUpdateCommand } from './patrons_update_command';
import type { PatronsUpdateProfile } from './patrons_update_profile';
import type { PayablesView } from './payables_view';
import type { PaymentDailyClosed } from './payment_daily_closed';
import type { PaymentExceptionOpened } from './payment_exception_opened';
import type { PaymentExceptionResolved } from './payment_exception_resolved';
import type { PaymentExpenseRecorded } from './payment_expense_recorded';
import type { PaymentFailed } from './payment_failed';
import type { PaymentMatched } from './payment_matched';
import type { PaymentPending } from './payment_pending';
import type { PaymentReceived } from './payment_received';
import type { PaymentRefunded } from './payment_refunded';
import type { PoChanged } from './po_changed';
import type { PoSupplierAdded } from './po_supplier_added';
import type { PoVarianceFound } from './po_variance_found';
import type { PoView } from './po_view';
import type { PrivacyErasePatron } from './privacy_erase_patron';
import type { PrivacyErased } from './privacy_erased';
import type { PrivacyExportPatron } from './privacy_export_patron';
import type { PrivacyExported } from './privacy_exported';
import type { PrivacySetDataSharing } from './privacy_set_data_sharing';
import type { PrivacySharingChanged } from './privacy_sharing_changed';
import type { Problem } from './problem';
import type { PromisesView } from './promises_view';
import type { PublicStorefront } from './public_storefront';
import type { ReportsView } from './reports_view';
import type { ResolutionView } from './resolution_view';
import type { RewardsConfigure } from './rewards_configure';
import type { RewardsRecordVisit } from './rewards_record_visit';
import type { RewardsRedeem } from './rewards_redeem';
import type { RxView } from './rx_view';
import type { SentinelCheck } from './sentinel_check';
import type { SentinelVerdict } from './sentinel_verdict';
import type { SessionResult } from './session_result';
import type { SettingsView } from './settings_view';
import type { SettlementRecorded } from './settlement_recorded';
import type { ShiftClose } from './shift_close';
import type { ShiftOpen } from './shift_open';
import type { ShiftView } from './shift_view';
import type { StaffAdd } from './staff_add';
import type { StaffAddCommand } from './staff_add_command';
import type { StaffAdded } from './staff_added';
import type { StaffLoggedIn } from './staff_logged_in';
import type { StaffLogin } from './staff_login';
import type { StaffLoginCommand } from './staff_login_command';
import type { StaffLogout } from './staff_logout';
import type { StaffSetSkills } from './staff_set_skills';
import type { StaffShiftClosed } from './staff_shift_closed';
import type { StaffShiftOpened } from './staff_shift_opened';
import type { StaffSkillsSet } from './staff_skills_set';
import type { StaffView } from './staff_view';
import type { StockAdjust } from './stock_adjust';
import type { StockChanged } from './stock_changed';
import type { StockCount } from './stock_count';
import type { StockDemandLogged } from './stock_demand_logged';
import type { StockLogUnmetDemand } from './stock_log_unmet_demand';
import type { StockOverrideRecorded } from './stock_override_recorded';
import type { StockRecallBatch } from './stock_recall_batch';
import type { StockReceive } from './stock_receive';
import type { StockView } from './stock_view';
import type { StorefrontPublish } from './storefront_publish';
import type { StorefrontPublished } from './storefront_published';
import type { StorefrontView } from './storefront_view';
import type { SuppliersView } from './suppliers_view';
import type { SupplyAddSupplier } from './supply_add_supplier';
import type { SupplyCancelPo } from './supply_cancel_po';
import type { SupplyConfirmPo } from './supply_confirm_po';
import type { SupplyDraftPo } from './supply_draft_po';
import type { SupplyPlacePo } from './supply_place_po';
import type { SupplyReceive } from './supply_receive';
import type { SupplyRecordBill } from './supply_record_bill';
import type { SupplyRecordQuote } from './supply_record_quote';
import type { SupplySendClaim } from './supply_send_claim';
import type { TaxInvoiceIssued } from './tax_invoice_issued';
import type { TreasuryDailyClose } from './treasury_daily_close';
import type { TreasuryExpense } from './treasury_expense';
import type { TreasuryMatchBill } from './treasury_match_bill';
import type { TreasuryMatchKhata } from './treasury_match_khata';
import type { TreasuryRailsEvent } from './treasury_rails_event';
import type { TreasuryRecordSettlement } from './treasury_record_settlement';
import type { TreasuryRefund } from './treasury_refund';
import type { TreasuryResolveException } from './treasury_resolve_exception';
import type { TrustView } from './trust_view';
import type { VerdictView } from './verdict_view';
import type { ViewInvalidate } from './view_invalidate';
import appointments_assignSchema from './schemas/appointments_assign.schema.json';
import appointments_bookSchema from './schemas/appointments_book.schema.json';
import appointments_transitionSchema from './schemas/appointments_transition.schema.json';
import appointments_viewSchema from './schemas/appointments_view.schema.json';
import appointments_walk_inSchema from './schemas/appointments_walk_in.schema.json';
import approvalSchema from './schemas/approval.schema.json';
import approval_decidedSchema from './schemas/approval_decided.schema.json';
import approval_requestedSchema from './schemas/approval_requested.schema.json';
import audit_verificationSchema from './schemas/audit_verification.schema.json';
import audit_verifiedSchema from './schemas/audit_verified.schema.json';
import batch_recalledSchema from './schemas/batch_recalled.schema.json';
import bill_changedSchema from './schemas/bill_changed.schema.json';
import bill_paidSchema from './schemas/bill_paid.schema.json';
import bill_paid_viewSchema from './schemas/bill_paid_view.schema.json';
import bill_pay_viewSchema from './schemas/bill_pay_view.schema.json';
import bill_price_overrideSchema from './schemas/bill_price_override.schema.json';
import bill_returnedSchema from './schemas/bill_returned.schema.json';
import bill_ticket_changedSchema from './schemas/bill_ticket_changed.schema.json';
import bill_viewSchema from './schemas/bill_view.schema.json';
import books_close_monthSchema from './schemas/books_close_month.schema.json';
import books_month_closedSchema from './schemas/books_month_closed.schema.json';
import capital_appliedSchema from './schemas/capital_applied.schema.json';
import capital_applySchema from './schemas/capital_apply.schema.json';
import capital_offer_receivedSchema from './schemas/capital_offer_received.schema.json';
import capital_record_offerSchema from './schemas/capital_record_offer.schema.json';
import capital_viewSchema from './schemas/capital_view.schema.json';
import catalog_add_itemSchema from './schemas/catalog_add_item.schema.json';
import catalog_bulk_priceSchema from './schemas/catalog_bulk_price.schema.json';
import catalog_change_priceSchema from './schemas/catalog_change_price.schema.json';
import catalog_import_itemsSchema from './schemas/catalog_import_items.schema.json';
import catalog_item_addedSchema from './schemas/catalog_item_added.schema.json';
import catalog_item_viewSchema from './schemas/catalog_item_view.schema.json';
import catalog_price_changedSchema from './schemas/catalog_price_changed.schema.json';
import catalog_search_viewSchema from './schemas/catalog_search_view.schema.json';
import claim_viewSchema from './schemas/claim_view.schema.json';
import commandSchema from './schemas/command.schema.json';
import command_executedSchema from './schemas/command_executed.schema.json';
import command_resultSchema from './schemas/command_result.schema.json';
import commonSchema from './schemas/common.schema.json';
import consent_grantSchema from './schemas/consent_grant.schema.json';
import consent_stopSchema from './schemas/consent_stop.schema.json';
import consent_withdrawSchema from './schemas/consent_withdraw.schema.json';
import counter_add_linesSchema from './schemas/counter_add_lines.schema.json';
import counter_advance_ticketSchema from './schemas/counter_advance_ticket.schema.json';
import counter_attach_patronSchema from './schemas/counter_attach_patron.schema.json';
import counter_checkoutSchema from './schemas/counter_checkout.schema.json';
import counter_checkout_khataSchema from './schemas/counter_checkout_khata.schema.json';
import counter_open_billSchema from './schemas/counter_open_bill.schema.json';
import counter_parkSchema from './schemas/counter_park.schema.json';
import counter_remove_lineSchema from './schemas/counter_remove_line.schema.json';
import counter_request_upiSchema from './schemas/counter_request_upi.schema.json';
import counter_resumeSchema from './schemas/counter_resume.schema.json';
import counter_returnSchema from './schemas/counter_return.schema.json';
import counter_send_to_kitchenSchema from './schemas/counter_send_to_kitchen.schema.json';
import counter_set_qtySchema from './schemas/counter_set_qty.schema.json';
import counter_undoSchema from './schemas/counter_undo.schema.json';
import counter_void_billSchema from './schemas/counter_void_bill.schema.json';
import credit_changedSchema from './schemas/credit_changed.schema.json';
import credit_payable_changedSchema from './schemas/credit_payable_changed.schema.json';
import credit_receipt_requestedSchema from './schemas/credit_receipt_requested.schema.json';
import credit_reminder_requestedSchema from './schemas/credit_reminder_requested.schema.json';
import credit_statement_requestedSchema from './schemas/credit_statement_requested.schema.json';
import customer_search_viewSchema from './schemas/customer_search_view.schema.json';
import demand_viewSchema from './schemas/demand_view.schema.json';
import device_health_reportedSchema from './schemas/device_health_reported.schema.json';
import device_report_healthSchema from './schemas/device_report_health.schema.json';
import envelopeSchema from './schemas/envelope.schema.json';
import eventSchema from './schemas/event.schema.json';
import expiry_viewSchema from './schemas/expiry_view.schema.json';
import feedback_recordSchema from './schemas/feedback_record.schema.json';
import feedback_recordedSchema from './schemas/feedback_recorded.schema.json';
import feedback_viewSchema from './schemas/feedback_view.schema.json';
import gate_viewSchema from './schemas/gate_view.schema.json';
import grn_viewSchema from './schemas/grn_view.schema.json';
import health_viewSchema from './schemas/health_view.schema.json';
import hisaab_viewSchema from './schemas/hisaab_view.schema.json';
import home_viewSchema from './schemas/home_view.schema.json';
import i18n_changedSchema from './schemas/i18n_changed.schema.json';
import khata_account_viewSchema from './schemas/khata_account_view.schema.json';
import khata_viewSchema from './schemas/khata_view.schema.json';
import kot_viewSchema from './schemas/kot_view.schema.json';
import layer_pending_viewSchema from './schemas/layer_pending_view.schema.json';
import ledger_acknowledge_entrySchema from './schemas/ledger_acknowledge_entry.schema.json';
import ledger_add_entrySchema from './schemas/ledger_add_entry.schema.json';
import ledger_add_payableSchema from './schemas/ledger_add_payable.schema.json';
import ledger_apply_advanceSchema from './schemas/ledger_apply_advance.schema.json';
import ledger_apply_verified_paymentSchema from './schemas/ledger_apply_verified_payment.schema.json';
import ledger_dispute_entrySchema from './schemas/ledger_dispute_entry.schema.json';
import ledger_open_accountSchema from './schemas/ledger_open_account.schema.json';
import ledger_pay_payableSchema from './schemas/ledger_pay_payable.schema.json';
import ledger_record_depositSchema from './schemas/ledger_record_deposit.schema.json';
import ledger_record_paymentSchema from './schemas/ledger_record_payment.schema.json';
import ledger_record_promiseSchema from './schemas/ledger_record_promise.schema.json';
import ledger_resolve_disputeSchema from './schemas/ledger_resolve_dispute.schema.json';
import ledger_reverse_entrySchema from './schemas/ledger_reverse_entry.schema.json';
import ledger_send_reminderSchema from './schemas/ledger_send_reminder.schema.json';
import ledger_send_statementSchema from './schemas/ledger_send_statement.schema.json';
import ledger_set_limitSchema from './schemas/ledger_set_limit.schema.json';
import ledger_statement_viewSchema from './schemas/ledger_statement_view.schema.json';
import merchant_bootstrapSchema from './schemas/merchant_bootstrap.schema.json';
import merchant_update_settingsSchema from './schemas/merchant_update_settings.schema.json';
import notifications_viewSchema from './schemas/notifications_view.schema.json';
import offer_cashback_requestedSchema from './schemas/offer_cashback_requested.schema.json';
import offer_clawed_backSchema from './schemas/offer_clawed_back.schema.json';
import offer_detail_viewSchema from './schemas/offer_detail_view.schema.json';
import offer_expiredSchema from './schemas/offer_expired.schema.json';
import offer_issuedSchema from './schemas/offer_issued.schema.json';
import offer_program_changedSchema from './schemas/offer_program_changed.schema.json';
import offer_redeemedSchema from './schemas/offer_redeemed.schema.json';
import offers_create_programSchema from './schemas/offers_create_program.schema.json';
import offers_exclude_payersSchema from './schemas/offers_exclude_payers.schema.json';
import offers_expire_dueSchema from './schemas/offers_expire_due.schema.json';
import offers_pause_programSchema from './schemas/offers_pause_program.schema.json';
import offers_viewSchema from './schemas/offers_view.schema.json';
import onboarding_complete_stepSchema from './schemas/onboarding_complete_step.schema.json';
import onboarding_startedSchema from './schemas/onboarding_started.schema.json';
import onboarding_updatedSchema from './schemas/onboarding_updated.schema.json';
import onboarding_viewSchema from './schemas/onboarding_view.schema.json';
import order_appointment_changedSchema from './schemas/order_appointment_changed.schema.json';
import order_changedSchema from './schemas/order_changed.schema.json';
import order_viewSchema from './schemas/order_view.schema.json';
import orders_acceptSchema from './schemas/orders_accept.schema.json';
import orders_advanceSchema from './schemas/orders_advance.schema.json';
import orders_create_draftSchema from './schemas/orders_create_draft.schema.json';
import orders_declineSchema from './schemas/orders_decline.schema.json';
import orders_placeSchema from './schemas/orders_place.schema.json';
import orders_settleSchema from './schemas/orders_settle.schema.json';
import orders_substituteSchema from './schemas/orders_substitute.schema.json';
import orders_viewSchema from './schemas/orders_view.schema.json';
import park_viewSchema from './schemas/park_view.schema.json';
import patron_changedSchema from './schemas/patron_changed.schema.json';
import patron_consent_changedSchema from './schemas/patron_consent_changed.schema.json';
import patron_exportSchema from './schemas/patron_export.schema.json';
import patron_mergedSchema from './schemas/patron_merged.schema.json';
import patron_reward_changedSchema from './schemas/patron_reward_changed.schema.json';
import patron_viewSchema from './schemas/patron_view.schema.json';
import patrons_addSchema from './schemas/patrons_add.schema.json';
import patrons_add_commandSchema from './schemas/patrons_add_command.schema.json';
import patrons_add_household_memberSchema from './schemas/patrons_add_household_member.schema.json';
import patrons_mergeSchema from './schemas/patrons_merge.schema.json';
import patrons_propose_mergeSchema from './schemas/patrons_propose_merge.schema.json';
import patrons_update_commandSchema from './schemas/patrons_update_command.schema.json';
import patrons_update_profileSchema from './schemas/patrons_update_profile.schema.json';
import payables_viewSchema from './schemas/payables_view.schema.json';
import payment_daily_closedSchema from './schemas/payment_daily_closed.schema.json';
import payment_exception_openedSchema from './schemas/payment_exception_opened.schema.json';
import payment_exception_resolvedSchema from './schemas/payment_exception_resolved.schema.json';
import payment_expense_recordedSchema from './schemas/payment_expense_recorded.schema.json';
import payment_failedSchema from './schemas/payment_failed.schema.json';
import payment_matchedSchema from './schemas/payment_matched.schema.json';
import payment_pendingSchema from './schemas/payment_pending.schema.json';
import payment_receivedSchema from './schemas/payment_received.schema.json';
import payment_refundedSchema from './schemas/payment_refunded.schema.json';
import po_changedSchema from './schemas/po_changed.schema.json';
import po_supplier_addedSchema from './schemas/po_supplier_added.schema.json';
import po_variance_foundSchema from './schemas/po_variance_found.schema.json';
import po_viewSchema from './schemas/po_view.schema.json';
import privacy_erase_patronSchema from './schemas/privacy_erase_patron.schema.json';
import privacy_erasedSchema from './schemas/privacy_erased.schema.json';
import privacy_export_patronSchema from './schemas/privacy_export_patron.schema.json';
import privacy_exportedSchema from './schemas/privacy_exported.schema.json';
import privacy_set_data_sharingSchema from './schemas/privacy_set_data_sharing.schema.json';
import privacy_sharing_changedSchema from './schemas/privacy_sharing_changed.schema.json';
import problemSchema from './schemas/problem.schema.json';
import promises_viewSchema from './schemas/promises_view.schema.json';
import public_storefrontSchema from './schemas/public_storefront.schema.json';
import reports_viewSchema from './schemas/reports_view.schema.json';
import resolution_viewSchema from './schemas/resolution_view.schema.json';
import rewards_configureSchema from './schemas/rewards_configure.schema.json';
import rewards_record_visitSchema from './schemas/rewards_record_visit.schema.json';
import rewards_redeemSchema from './schemas/rewards_redeem.schema.json';
import rx_viewSchema from './schemas/rx_view.schema.json';
import sentinel_checkSchema from './schemas/sentinel_check.schema.json';
import sentinel_verdictSchema from './schemas/sentinel_verdict.schema.json';
import session_resultSchema from './schemas/session_result.schema.json';
import settings_viewSchema from './schemas/settings_view.schema.json';
import settlement_recordedSchema from './schemas/settlement_recorded.schema.json';
import shift_closeSchema from './schemas/shift_close.schema.json';
import shift_openSchema from './schemas/shift_open.schema.json';
import shift_viewSchema from './schemas/shift_view.schema.json';
import staff_addSchema from './schemas/staff_add.schema.json';
import staff_add_commandSchema from './schemas/staff_add_command.schema.json';
import staff_addedSchema from './schemas/staff_added.schema.json';
import staff_logged_inSchema from './schemas/staff_logged_in.schema.json';
import staff_loginSchema from './schemas/staff_login.schema.json';
import staff_login_commandSchema from './schemas/staff_login_command.schema.json';
import staff_logoutSchema from './schemas/staff_logout.schema.json';
import staff_set_skillsSchema from './schemas/staff_set_skills.schema.json';
import staff_shift_closedSchema from './schemas/staff_shift_closed.schema.json';
import staff_shift_openedSchema from './schemas/staff_shift_opened.schema.json';
import staff_skills_setSchema from './schemas/staff_skills_set.schema.json';
import staff_viewSchema from './schemas/staff_view.schema.json';
import stock_adjustSchema from './schemas/stock_adjust.schema.json';
import stock_changedSchema from './schemas/stock_changed.schema.json';
import stock_countSchema from './schemas/stock_count.schema.json';
import stock_demand_loggedSchema from './schemas/stock_demand_logged.schema.json';
import stock_log_unmet_demandSchema from './schemas/stock_log_unmet_demand.schema.json';
import stock_override_recordedSchema from './schemas/stock_override_recorded.schema.json';
import stock_recall_batchSchema from './schemas/stock_recall_batch.schema.json';
import stock_receiveSchema from './schemas/stock_receive.schema.json';
import stock_viewSchema from './schemas/stock_view.schema.json';
import storefront_publishSchema from './schemas/storefront_publish.schema.json';
import storefront_publishedSchema from './schemas/storefront_published.schema.json';
import storefront_viewSchema from './schemas/storefront_view.schema.json';
import suppliers_viewSchema from './schemas/suppliers_view.schema.json';
import supply_add_supplierSchema from './schemas/supply_add_supplier.schema.json';
import supply_cancel_poSchema from './schemas/supply_cancel_po.schema.json';
import supply_confirm_poSchema from './schemas/supply_confirm_po.schema.json';
import supply_draft_poSchema from './schemas/supply_draft_po.schema.json';
import supply_place_poSchema from './schemas/supply_place_po.schema.json';
import supply_receiveSchema from './schemas/supply_receive.schema.json';
import supply_record_billSchema from './schemas/supply_record_bill.schema.json';
import supply_record_quoteSchema from './schemas/supply_record_quote.schema.json';
import supply_send_claimSchema from './schemas/supply_send_claim.schema.json';
import tax_invoice_issuedSchema from './schemas/tax_invoice_issued.schema.json';
import treasury_daily_closeSchema from './schemas/treasury_daily_close.schema.json';
import treasury_expenseSchema from './schemas/treasury_expense.schema.json';
import treasury_match_billSchema from './schemas/treasury_match_bill.schema.json';
import treasury_match_khataSchema from './schemas/treasury_match_khata.schema.json';
import treasury_rails_eventSchema from './schemas/treasury_rails_event.schema.json';
import treasury_record_settlementSchema from './schemas/treasury_record_settlement.schema.json';
import treasury_refundSchema from './schemas/treasury_refund.schema.json';
import treasury_resolve_exceptionSchema from './schemas/treasury_resolve_exception.schema.json';
import trust_viewSchema from './schemas/trust_view.schema.json';
import verdict_viewSchema from './schemas/verdict_view.schema.json';
import view_invalidateSchema from './schemas/view_invalidate.schema.json';

export type { AppointmentsAssign } from './appointments_assign';
export type { AppointmentsBook } from './appointments_book';
export type { AppointmentsTransition } from './appointments_transition';
export type { AppointmentsView } from './appointments_view';
export type { AppointmentsWalkIn } from './appointments_walk_in';
export type { ApprovalRequest } from './approval';
export type { ApprovalDecided } from './approval_decided';
export type { ApprovalRequested } from './approval_requested';
export type { AuditVerification } from './audit_verification';
export type { AuditVerified } from './audit_verified';
export type { BatchRecalled } from './batch_recalled';
export type { BillChanged } from './bill_changed';
export type { BillPaid } from './bill_paid';
export type { BillPaidView } from './bill_paid_view';
export type { BillPayView } from './bill_pay_view';
export type { BillPriceOverride } from './bill_price_override';
export type { BillReturned } from './bill_returned';
export type { BillTicketChanged } from './bill_ticket_changed';
export type { BillView } from './bill_view';
export type { BooksCloseMonth } from './books_close_month';
export type { BooksMonthClosed } from './books_month_closed';
export type { CapitalApplied } from './capital_applied';
export type { CapitalApply } from './capital_apply';
export type { CapitalOfferReceived } from './capital_offer_received';
export type { CapitalRecordOffer } from './capital_record_offer';
export type { CapitalView } from './capital_view';
export type { CatalogAddItem } from './catalog_add_item';
export type { CatalogBulkPrice } from './catalog_bulk_price';
export type { CatalogChangePrice } from './catalog_change_price';
export type { CatalogImportItems } from './catalog_import_items';
export type { CatalogItemAdded } from './catalog_item_added';
export type { CatalogItemView } from './catalog_item_view';
export type { CatalogPriceChanged } from './catalog_price_changed';
export type { CatalogSearchView } from './catalog_search_view';
export type { ClaimView } from './claim_view';
export type { CommandRequest } from './command';
export type { CommandExecuted } from './command_executed';
export type { CommandResult } from './command_result';
export type { Common } from './common';
export type { ConsentGrant } from './consent_grant';
export type { ConsentStop } from './consent_stop';
export type { ConsentWithdraw } from './consent_withdraw';
export type { CounterAddLines } from './counter_add_lines';
export type { CounterAdvanceTicket } from './counter_advance_ticket';
export type { CounterAttachPatron } from './counter_attach_patron';
export type { CounterCheckout } from './counter_checkout';
export type { CounterCheckoutKhata } from './counter_checkout_khata';
export type { CounterOpenBill } from './counter_open_bill';
export type { CounterPark } from './counter_park';
export type { CounterRemoveLine } from './counter_remove_line';
export type { CounterRequestUpi } from './counter_request_upi';
export type { CounterResume } from './counter_resume';
export type { CounterReturn } from './counter_return';
export type { CounterSendToKitchen } from './counter_send_to_kitchen';
export type { CounterSetQty } from './counter_set_qty';
export type { CounterUndo } from './counter_undo';
export type { CounterVoidBill } from './counter_void_bill';
export type { CreditChanged } from './credit_changed';
export type { CreditPayableChanged } from './credit_payable_changed';
export type { CreditReceiptRequested } from './credit_receipt_requested';
export type { CreditReminderRequested } from './credit_reminder_requested';
export type { CreditStatementRequested } from './credit_statement_requested';
export type { CustomerSearchView } from './customer_search_view';
export type { DemandView } from './demand_view';
export type { DeviceHealthReported } from './device_health_reported';
export type { DeviceReportHealth } from './device_report_health';
export type { Envelope } from './envelope';
export type { DomainEvent } from './event';
export type { ExpiryView } from './expiry_view';
export type { FeedbackRecord } from './feedback_record';
export type { FeedbackRecorded } from './feedback_recorded';
export type { FeedbackView } from './feedback_view';
export type { GateView } from './gate_view';
export type { GrnView } from './grn_view';
export type { HealthView } from './health_view';
export type { HisaabView } from './hisaab_view';
export type { HomeView } from './home_view';
export type { LanguageChanged } from './i18n_changed';
export type { KhataAccountView } from './khata_account_view';
export type { KhataView } from './khata_view';
export type { KotView } from './kot_view';
export type { LayerPendingView } from './layer_pending_view';
export type { LedgerAcknowledgeEntry } from './ledger_acknowledge_entry';
export type { LedgerAddEntry } from './ledger_add_entry';
export type { LedgerAddPayable } from './ledger_add_payable';
export type { LedgerApplyAdvance } from './ledger_apply_advance';
export type { LedgerApplyVerifiedPayment } from './ledger_apply_verified_payment';
export type { LedgerDisputeEntry } from './ledger_dispute_entry';
export type { LedgerOpenAccount } from './ledger_open_account';
export type { LedgerPayPayable } from './ledger_pay_payable';
export type { LedgerRecordDeposit } from './ledger_record_deposit';
export type { LedgerRecordPayment } from './ledger_record_payment';
export type { LedgerRecordPromise } from './ledger_record_promise';
export type { LedgerResolveDispute } from './ledger_resolve_dispute';
export type { LedgerReverseEntry } from './ledger_reverse_entry';
export type { LedgerSendReminder } from './ledger_send_reminder';
export type { LedgerSendStatement } from './ledger_send_statement';
export type { LedgerSetLimit } from './ledger_set_limit';
export type { LedgerStatementView } from './ledger_statement_view';
export type { MerchantBootstrap } from './merchant_bootstrap';
export type { MerchantUpdateSettings } from './merchant_update_settings';
export type { NotificationsView } from './notifications_view';
export type { OfferCashbackRequested } from './offer_cashback_requested';
export type { OfferClawedBack } from './offer_clawed_back';
export type { OfferDetailView } from './offer_detail_view';
export type { OfferExpired } from './offer_expired';
export type { OfferIssued } from './offer_issued';
export type { OfferProgramChanged } from './offer_program_changed';
export type { OfferRedeemed } from './offer_redeemed';
export type { OffersCreateProgram } from './offers_create_program';
export type { OffersExcludePayers } from './offers_exclude_payers';
export type { OffersExpireDue } from './offers_expire_due';
export type { OffersPauseProgram } from './offers_pause_program';
export type { OffersView } from './offers_view';
export type { OnboardingCompleteStep } from './onboarding_complete_step';
export type { OnboardingStarted } from './onboarding_started';
export type { OnboardingUpdated } from './onboarding_updated';
export type { OnboardingView } from './onboarding_view';
export type { OrderAppointmentChanged } from './order_appointment_changed';
export type { OrderChanged } from './order_changed';
export type { OrderView } from './order_view';
export type { OrdersAccept } from './orders_accept';
export type { OrdersAdvance } from './orders_advance';
export type { OrdersCreateDraft } from './orders_create_draft';
export type { OrdersDecline } from './orders_decline';
export type { OrdersPlace } from './orders_place';
export type { OrdersSettle } from './orders_settle';
export type { OrdersSubstitute } from './orders_substitute';
export type { OrdersView } from './orders_view';
export type { ParkView } from './park_view';
export type { PatronChanged } from './patron_changed';
export type { PatronConsentChanged } from './patron_consent_changed';
export type { PatronExport } from './patron_export';
export type { PatronMerged } from './patron_merged';
export type { PatronRewardChanged } from './patron_reward_changed';
export type { PatronView } from './patron_view';
export type { PatronsAdd } from './patrons_add';
export type { PatronsAddCommand } from './patrons_add_command';
export type { PatronsAddHouseholdMember } from './patrons_add_household_member';
export type { PatronsMerge } from './patrons_merge';
export type { PatronsProposeMerge } from './patrons_propose_merge';
export type { PatronsUpdateCommand } from './patrons_update_command';
export type { PatronsUpdateProfile } from './patrons_update_profile';
export type { PayablesView } from './payables_view';
export type { PaymentDailyClosed } from './payment_daily_closed';
export type { PaymentExceptionOpened } from './payment_exception_opened';
export type { PaymentExceptionResolved } from './payment_exception_resolved';
export type { PaymentExpenseRecorded } from './payment_expense_recorded';
export type { PaymentFailed } from './payment_failed';
export type { PaymentMatched } from './payment_matched';
export type { PaymentPending } from './payment_pending';
export type { PaymentReceived } from './payment_received';
export type { PaymentRefunded } from './payment_refunded';
export type { PoChanged } from './po_changed';
export type { PoSupplierAdded } from './po_supplier_added';
export type { PoVarianceFound } from './po_variance_found';
export type { PoView } from './po_view';
export type { PrivacyErasePatron } from './privacy_erase_patron';
export type { PrivacyErased } from './privacy_erased';
export type { PrivacyExportPatron } from './privacy_export_patron';
export type { PrivacyExported } from './privacy_exported';
export type { PrivacySetDataSharing } from './privacy_set_data_sharing';
export type { PrivacySharingChanged } from './privacy_sharing_changed';
export type { Problem } from './problem';
export type { PromisesView } from './promises_view';
export type { PublicStorefront } from './public_storefront';
export type { ReportsView } from './reports_view';
export type { ResolutionView } from './resolution_view';
export type { RewardsConfigure } from './rewards_configure';
export type { RewardsRecordVisit } from './rewards_record_visit';
export type { RewardsRedeem } from './rewards_redeem';
export type { RxView } from './rx_view';
export type { SentinelCheck } from './sentinel_check';
export type { SentinelVerdict } from './sentinel_verdict';
export type { SessionResult } from './session_result';
export type { SettingsView } from './settings_view';
export type { SettlementRecorded } from './settlement_recorded';
export type { ShiftClose } from './shift_close';
export type { ShiftOpen } from './shift_open';
export type { ShiftView } from './shift_view';
export type { StaffAdd } from './staff_add';
export type { StaffAddCommand } from './staff_add_command';
export type { StaffAdded } from './staff_added';
export type { StaffLoggedIn } from './staff_logged_in';
export type { StaffLogin } from './staff_login';
export type { StaffLoginCommand } from './staff_login_command';
export type { StaffLogout } from './staff_logout';
export type { StaffSetSkills } from './staff_set_skills';
export type { StaffShiftClosed } from './staff_shift_closed';
export type { StaffShiftOpened } from './staff_shift_opened';
export type { StaffSkillsSet } from './staff_skills_set';
export type { StaffView } from './staff_view';
export type { StockAdjust } from './stock_adjust';
export type { StockChanged } from './stock_changed';
export type { StockCount } from './stock_count';
export type { StockDemandLogged } from './stock_demand_logged';
export type { StockLogUnmetDemand } from './stock_log_unmet_demand';
export type { StockOverrideRecorded } from './stock_override_recorded';
export type { StockRecallBatch } from './stock_recall_batch';
export type { StockReceive } from './stock_receive';
export type { StockView } from './stock_view';
export type { StorefrontPublish } from './storefront_publish';
export type { StorefrontPublished } from './storefront_published';
export type { StorefrontView } from './storefront_view';
export type { SuppliersView } from './suppliers_view';
export type { SupplyAddSupplier } from './supply_add_supplier';
export type { SupplyCancelPo } from './supply_cancel_po';
export type { SupplyConfirmPo } from './supply_confirm_po';
export type { SupplyDraftPo } from './supply_draft_po';
export type { SupplyPlacePo } from './supply_place_po';
export type { SupplyReceive } from './supply_receive';
export type { SupplyRecordBill } from './supply_record_bill';
export type { SupplyRecordQuote } from './supply_record_quote';
export type { SupplySendClaim } from './supply_send_claim';
export type { TaxInvoiceIssued } from './tax_invoice_issued';
export type { TreasuryDailyClose } from './treasury_daily_close';
export type { TreasuryExpense } from './treasury_expense';
export type { TreasuryMatchBill } from './treasury_match_bill';
export type { TreasuryMatchKhata } from './treasury_match_khata';
export type { TreasuryRailsEvent } from './treasury_rails_event';
export type { TreasuryRecordSettlement } from './treasury_record_settlement';
export type { TreasuryRefund } from './treasury_refund';
export type { TreasuryResolveException } from './treasury_resolve_exception';
export type { TrustView } from './trust_view';
export type { VerdictView } from './verdict_view';
export type { ViewInvalidate } from './view_invalidate';
export type * from './common'; // shared definitions: Locale, SpeechLocale, Audience, Tier, ...

/** Every contract: name (file stem), JSON Schema $id and the schema itself, for Ajv. */
export const SCHEMAS = [
  { name: 'appointments_assign', id: 'https://arth.local/contracts/commands/appointments_assign.schema.json', schema: appointments_assignSchema },
  { name: 'appointments_book', id: 'https://arth.local/contracts/commands/appointments_book.schema.json', schema: appointments_bookSchema },
  { name: 'appointments_transition', id: 'https://arth.local/contracts/commands/appointments_transition.schema.json', schema: appointments_transitionSchema },
  { name: 'appointments_view', id: 'https://arth.local/contracts/appointments_view.schema.json', schema: appointments_viewSchema },
  { name: 'appointments_walk_in', id: 'https://arth.local/contracts/commands/appointments_walk_in.schema.json', schema: appointments_walk_inSchema },
  { name: 'approval', id: 'https://arth.local/contracts/approval.schema.json', schema: approvalSchema },
  { name: 'approval_decided', id: 'https://arth.local/contracts/events/approval_decided.schema.json', schema: approval_decidedSchema },
  { name: 'approval_requested', id: 'https://arth.local/contracts/events/approval_requested.schema.json', schema: approval_requestedSchema },
  { name: 'audit_verification', id: 'https://arth.local/contracts/audit_verification.schema.json', schema: audit_verificationSchema },
  { name: 'audit_verified', id: 'https://arth.local/contracts/events/audit_verified.schema.json', schema: audit_verifiedSchema },
  { name: 'batch_recalled', id: 'https://arth.local/contracts/events/batch_recalled.schema.json', schema: batch_recalledSchema },
  { name: 'bill_changed', id: 'https://arth.local/contracts/events/bill_changed.schema.json', schema: bill_changedSchema },
  { name: 'bill_paid', id: 'https://arth.local/contracts/events/bill_paid.schema.json', schema: bill_paidSchema },
  { name: 'bill_paid_view', id: 'https://arth.local/contracts/bill_paid_view.schema.json', schema: bill_paid_viewSchema },
  { name: 'bill_pay_view', id: 'https://arth.local/contracts/bill_pay_view.schema.json', schema: bill_pay_viewSchema },
  { name: 'bill_price_override', id: 'https://arth.local/contracts/events/bill_price_override.schema.json', schema: bill_price_overrideSchema },
  { name: 'bill_returned', id: 'https://arth.local/contracts/events/bill_returned.schema.json', schema: bill_returnedSchema },
  { name: 'bill_ticket_changed', id: 'https://arth.local/contracts/events/bill_ticket_changed.schema.json', schema: bill_ticket_changedSchema },
  { name: 'bill_view', id: 'https://arth.local/contracts/bill_view.schema.json', schema: bill_viewSchema },
  { name: 'books_close_month', id: 'https://arth.local/contracts/commands/books_close_month.schema.json', schema: books_close_monthSchema },
  { name: 'books_month_closed', id: 'https://arth.local/contracts/events/books_month_closed.schema.json', schema: books_month_closedSchema },
  { name: 'capital_applied', id: 'https://arth.local/contracts/events/capital_applied.schema.json', schema: capital_appliedSchema },
  { name: 'capital_apply', id: 'https://arth.local/contracts/commands/capital_apply.schema.json', schema: capital_applySchema },
  { name: 'capital_offer_received', id: 'https://arth.local/contracts/events/capital_offer_received.schema.json', schema: capital_offer_receivedSchema },
  { name: 'capital_record_offer', id: 'https://arth.local/contracts/commands/capital_record_offer.schema.json', schema: capital_record_offerSchema },
  { name: 'capital_view', id: 'https://arth.local/contracts/capital_view.schema.json', schema: capital_viewSchema },
  { name: 'catalog_add_item', id: 'https://arth.local/contracts/commands/catalog_add_item.schema.json', schema: catalog_add_itemSchema },
  { name: 'catalog_bulk_price', id: 'https://arth.local/contracts/commands/catalog_bulk_price.schema.json', schema: catalog_bulk_priceSchema },
  { name: 'catalog_change_price', id: 'https://arth.local/contracts/commands/catalog_change_price.schema.json', schema: catalog_change_priceSchema },
  { name: 'catalog_import_items', id: 'https://arth.local/contracts/commands/catalog_import_items.schema.json', schema: catalog_import_itemsSchema },
  { name: 'catalog_item_added', id: 'https://arth.local/contracts/events/catalog_item_added.schema.json', schema: catalog_item_addedSchema },
  { name: 'catalog_item_view', id: 'https://arth.local/contracts/catalog_item_view.schema.json', schema: catalog_item_viewSchema },
  { name: 'catalog_price_changed', id: 'https://arth.local/contracts/events/catalog_price_changed.schema.json', schema: catalog_price_changedSchema },
  { name: 'catalog_search_view', id: 'https://arth.local/contracts/catalog_search_view.schema.json', schema: catalog_search_viewSchema },
  { name: 'claim_view', id: 'https://arth.local/contracts/claim_view.schema.json', schema: claim_viewSchema },
  { name: 'command', id: 'https://arth.local/contracts/command.schema.json', schema: commandSchema },
  { name: 'command_executed', id: 'https://arth.local/contracts/events/command_executed.schema.json', schema: command_executedSchema },
  { name: 'command_result', id: 'https://arth.local/contracts/command_result.schema.json', schema: command_resultSchema },
  { name: 'common', id: 'https://arth.local/contracts/common.schema.json', schema: commonSchema },
  { name: 'consent_grant', id: 'https://arth.local/contracts/commands/consent_grant.schema.json', schema: consent_grantSchema },
  { name: 'consent_stop', id: 'https://arth.local/contracts/commands/consent_stop.schema.json', schema: consent_stopSchema },
  { name: 'consent_withdraw', id: 'https://arth.local/contracts/commands/consent_withdraw.schema.json', schema: consent_withdrawSchema },
  { name: 'counter_add_lines', id: 'https://arth.local/contracts/commands/counter_add_lines.schema.json', schema: counter_add_linesSchema },
  { name: 'counter_advance_ticket', id: 'https://arth.local/contracts/commands/counter_advance_ticket.schema.json', schema: counter_advance_ticketSchema },
  { name: 'counter_attach_patron', id: 'https://arth.local/contracts/commands/counter_attach_patron.schema.json', schema: counter_attach_patronSchema },
  { name: 'counter_checkout', id: 'https://arth.local/contracts/commands/counter_checkout.schema.json', schema: counter_checkoutSchema },
  { name: 'counter_checkout_khata', id: 'https://arth.local/contracts/commands/counter_checkout_khata.schema.json', schema: counter_checkout_khataSchema },
  { name: 'counter_open_bill', id: 'https://arth.local/contracts/commands/counter_open_bill.schema.json', schema: counter_open_billSchema },
  { name: 'counter_park', id: 'https://arth.local/contracts/commands/counter_park.schema.json', schema: counter_parkSchema },
  { name: 'counter_remove_line', id: 'https://arth.local/contracts/commands/counter_remove_line.schema.json', schema: counter_remove_lineSchema },
  { name: 'counter_request_upi', id: 'https://arth.local/contracts/commands/counter_request_upi.schema.json', schema: counter_request_upiSchema },
  { name: 'counter_resume', id: 'https://arth.local/contracts/commands/counter_resume.schema.json', schema: counter_resumeSchema },
  { name: 'counter_return', id: 'https://arth.local/contracts/commands/counter_return.schema.json', schema: counter_returnSchema },
  { name: 'counter_send_to_kitchen', id: 'https://arth.local/contracts/commands/counter_send_to_kitchen.schema.json', schema: counter_send_to_kitchenSchema },
  { name: 'counter_set_qty', id: 'https://arth.local/contracts/commands/counter_set_qty.schema.json', schema: counter_set_qtySchema },
  { name: 'counter_undo', id: 'https://arth.local/contracts/commands/counter_undo.schema.json', schema: counter_undoSchema },
  { name: 'counter_void_bill', id: 'https://arth.local/contracts/commands/counter_void_bill.schema.json', schema: counter_void_billSchema },
  { name: 'credit_changed', id: 'https://arth.local/contracts/events/credit_changed.schema.json', schema: credit_changedSchema },
  { name: 'credit_payable_changed', id: 'https://arth.local/contracts/events/credit_payable_changed.schema.json', schema: credit_payable_changedSchema },
  { name: 'credit_receipt_requested', id: 'https://arth.local/contracts/events/credit_receipt_requested.schema.json', schema: credit_receipt_requestedSchema },
  { name: 'credit_reminder_requested', id: 'https://arth.local/contracts/events/credit_reminder_requested.schema.json', schema: credit_reminder_requestedSchema },
  { name: 'credit_statement_requested', id: 'https://arth.local/contracts/events/credit_statement_requested.schema.json', schema: credit_statement_requestedSchema },
  { name: 'customer_search_view', id: 'https://arth.local/contracts/customer_search_view.schema.json', schema: customer_search_viewSchema },
  { name: 'demand_view', id: 'https://arth.local/contracts/demand_view.schema.json', schema: demand_viewSchema },
  { name: 'device_health_reported', id: 'https://arth.local/contracts/events/device_health_reported.schema.json', schema: device_health_reportedSchema },
  { name: 'device_report_health', id: 'https://arth.local/contracts/commands/device_report_health.schema.json', schema: device_report_healthSchema },
  { name: 'envelope', id: 'https://arth.local/contracts/envelope.schema.json', schema: envelopeSchema },
  { name: 'event', id: 'https://arth.local/contracts/events/event.schema.json', schema: eventSchema },
  { name: 'expiry_view', id: 'https://arth.local/contracts/expiry_view.schema.json', schema: expiry_viewSchema },
  { name: 'feedback_record', id: 'https://arth.local/contracts/commands/feedback_record.schema.json', schema: feedback_recordSchema },
  { name: 'feedback_recorded', id: 'https://arth.local/contracts/events/feedback_recorded.schema.json', schema: feedback_recordedSchema },
  { name: 'feedback_view', id: 'https://arth.local/contracts/feedback_view.schema.json', schema: feedback_viewSchema },
  { name: 'gate_view', id: 'https://arth.local/contracts/gate_view.schema.json', schema: gate_viewSchema },
  { name: 'grn_view', id: 'https://arth.local/contracts/grn_view.schema.json', schema: grn_viewSchema },
  { name: 'health_view', id: 'https://arth.local/contracts/health_view.schema.json', schema: health_viewSchema },
  { name: 'hisaab_view', id: 'https://arth.local/contracts/hisaab_view.schema.json', schema: hisaab_viewSchema },
  { name: 'home_view', id: 'https://arth.local/contracts/home_view.schema.json', schema: home_viewSchema },
  { name: 'i18n_changed', id: 'https://arth.local/contracts/events/i18n_changed.schema.json', schema: i18n_changedSchema },
  { name: 'khata_account_view', id: 'https://arth.local/contracts/khata_account_view.schema.json', schema: khata_account_viewSchema },
  { name: 'khata_view', id: 'https://arth.local/contracts/khata_view.schema.json', schema: khata_viewSchema },
  { name: 'kot_view', id: 'https://arth.local/contracts/kot_view.schema.json', schema: kot_viewSchema },
  { name: 'layer_pending_view', id: 'https://arth.local/contracts/layer_pending_view.schema.json', schema: layer_pending_viewSchema },
  { name: 'ledger_acknowledge_entry', id: 'https://arth.local/contracts/commands/ledger_acknowledge_entry.schema.json', schema: ledger_acknowledge_entrySchema },
  { name: 'ledger_add_entry', id: 'https://arth.local/contracts/commands/ledger_add_entry.schema.json', schema: ledger_add_entrySchema },
  { name: 'ledger_add_payable', id: 'https://arth.local/contracts/commands/ledger_add_payable.schema.json', schema: ledger_add_payableSchema },
  { name: 'ledger_apply_advance', id: 'https://arth.local/contracts/commands/ledger_apply_advance.schema.json', schema: ledger_apply_advanceSchema },
  { name: 'ledger_apply_verified_payment', id: 'https://arth.local/contracts/commands/ledger_apply_verified_payment.schema.json', schema: ledger_apply_verified_paymentSchema },
  { name: 'ledger_dispute_entry', id: 'https://arth.local/contracts/commands/ledger_dispute_entry.schema.json', schema: ledger_dispute_entrySchema },
  { name: 'ledger_open_account', id: 'https://arth.local/contracts/commands/ledger_open_account.schema.json', schema: ledger_open_accountSchema },
  { name: 'ledger_pay_payable', id: 'https://arth.local/contracts/commands/ledger_pay_payable.schema.json', schema: ledger_pay_payableSchema },
  { name: 'ledger_record_deposit', id: 'https://arth.local/contracts/commands/ledger_record_deposit.schema.json', schema: ledger_record_depositSchema },
  { name: 'ledger_record_payment', id: 'https://arth.local/contracts/commands/ledger_record_payment.schema.json', schema: ledger_record_paymentSchema },
  { name: 'ledger_record_promise', id: 'https://arth.local/contracts/commands/ledger_record_promise.schema.json', schema: ledger_record_promiseSchema },
  { name: 'ledger_resolve_dispute', id: 'https://arth.local/contracts/commands/ledger_resolve_dispute.schema.json', schema: ledger_resolve_disputeSchema },
  { name: 'ledger_reverse_entry', id: 'https://arth.local/contracts/commands/ledger_reverse_entry.schema.json', schema: ledger_reverse_entrySchema },
  { name: 'ledger_send_reminder', id: 'https://arth.local/contracts/commands/ledger_send_reminder.schema.json', schema: ledger_send_reminderSchema },
  { name: 'ledger_send_statement', id: 'https://arth.local/contracts/commands/ledger_send_statement.schema.json', schema: ledger_send_statementSchema },
  { name: 'ledger_set_limit', id: 'https://arth.local/contracts/commands/ledger_set_limit.schema.json', schema: ledger_set_limitSchema },
  { name: 'ledger_statement_view', id: 'https://arth.local/contracts/ledger_statement_view.schema.json', schema: ledger_statement_viewSchema },
  { name: 'merchant_bootstrap', id: 'https://arth.local/contracts/commands/merchant_bootstrap.schema.json', schema: merchant_bootstrapSchema },
  { name: 'merchant_update_settings', id: 'https://arth.local/contracts/commands/merchant_update_settings.schema.json', schema: merchant_update_settingsSchema },
  { name: 'notifications_view', id: 'https://arth.local/contracts/notifications_view.schema.json', schema: notifications_viewSchema },
  { name: 'offer_cashback_requested', id: 'https://arth.local/contracts/events/offer_cashback_requested.schema.json', schema: offer_cashback_requestedSchema },
  { name: 'offer_clawed_back', id: 'https://arth.local/contracts/events/offer_clawed_back.schema.json', schema: offer_clawed_backSchema },
  { name: 'offer_detail_view', id: 'https://arth.local/contracts/offer_detail_view.schema.json', schema: offer_detail_viewSchema },
  { name: 'offer_expired', id: 'https://arth.local/contracts/events/offer_expired.schema.json', schema: offer_expiredSchema },
  { name: 'offer_issued', id: 'https://arth.local/contracts/events/offer_issued.schema.json', schema: offer_issuedSchema },
  { name: 'offer_program_changed', id: 'https://arth.local/contracts/events/offer_program_changed.schema.json', schema: offer_program_changedSchema },
  { name: 'offer_redeemed', id: 'https://arth.local/contracts/events/offer_redeemed.schema.json', schema: offer_redeemedSchema },
  { name: 'offers_create_program', id: 'https://arth.local/contracts/commands/offers_create_program.schema.json', schema: offers_create_programSchema },
  { name: 'offers_exclude_payers', id: 'https://arth.local/contracts/commands/offers_exclude_payers.schema.json', schema: offers_exclude_payersSchema },
  { name: 'offers_expire_due', id: 'https://arth.local/contracts/commands/offers_expire_due.schema.json', schema: offers_expire_dueSchema },
  { name: 'offers_pause_program', id: 'https://arth.local/contracts/commands/offers_pause_program.schema.json', schema: offers_pause_programSchema },
  { name: 'offers_view', id: 'https://arth.local/contracts/offers_view.schema.json', schema: offers_viewSchema },
  { name: 'onboarding_complete_step', id: 'https://arth.local/contracts/commands/onboarding_complete_step.schema.json', schema: onboarding_complete_stepSchema },
  { name: 'onboarding_started', id: 'https://arth.local/contracts/events/onboarding_started.schema.json', schema: onboarding_startedSchema },
  { name: 'onboarding_updated', id: 'https://arth.local/contracts/events/onboarding_updated.schema.json', schema: onboarding_updatedSchema },
  { name: 'onboarding_view', id: 'https://arth.local/contracts/onboarding_view.schema.json', schema: onboarding_viewSchema },
  { name: 'order_appointment_changed', id: 'https://arth.local/contracts/events/order_appointment_changed.schema.json', schema: order_appointment_changedSchema },
  { name: 'order_changed', id: 'https://arth.local/contracts/events/order_changed.schema.json', schema: order_changedSchema },
  { name: 'order_view', id: 'https://arth.local/contracts/order_view.schema.json', schema: order_viewSchema },
  { name: 'orders_accept', id: 'https://arth.local/contracts/commands/orders_accept.schema.json', schema: orders_acceptSchema },
  { name: 'orders_advance', id: 'https://arth.local/contracts/commands/orders_advance.schema.json', schema: orders_advanceSchema },
  { name: 'orders_create_draft', id: 'https://arth.local/contracts/commands/orders_create_draft.schema.json', schema: orders_create_draftSchema },
  { name: 'orders_decline', id: 'https://arth.local/contracts/commands/orders_decline.schema.json', schema: orders_declineSchema },
  { name: 'orders_place', id: 'https://arth.local/contracts/commands/orders_place.schema.json', schema: orders_placeSchema },
  { name: 'orders_settle', id: 'https://arth.local/contracts/commands/orders_settle.schema.json', schema: orders_settleSchema },
  { name: 'orders_substitute', id: 'https://arth.local/contracts/commands/orders_substitute.schema.json', schema: orders_substituteSchema },
  { name: 'orders_view', id: 'https://arth.local/contracts/orders_view.schema.json', schema: orders_viewSchema },
  { name: 'park_view', id: 'https://arth.local/contracts/park_view.schema.json', schema: park_viewSchema },
  { name: 'patron_changed', id: 'https://arth.local/contracts/events/patron_changed.schema.json', schema: patron_changedSchema },
  { name: 'patron_consent_changed', id: 'https://arth.local/contracts/events/patron_consent_changed.schema.json', schema: patron_consent_changedSchema },
  { name: 'patron_export', id: 'https://arth.local/contracts/patron_export.schema.json', schema: patron_exportSchema },
  { name: 'patron_merged', id: 'https://arth.local/contracts/events/patron_merged.schema.json', schema: patron_mergedSchema },
  { name: 'patron_reward_changed', id: 'https://arth.local/contracts/events/patron_reward_changed.schema.json', schema: patron_reward_changedSchema },
  { name: 'patron_view', id: 'https://arth.local/contracts/patron_view.schema.json', schema: patron_viewSchema },
  { name: 'patrons_add', id: 'https://arth.local/contracts/commands/patrons_add.schema.json', schema: patrons_addSchema },
  { name: 'patrons_add_command', id: 'https://arth.local/contracts/commands/patrons_add_command.schema.json', schema: patrons_add_commandSchema },
  { name: 'patrons_add_household_member', id: 'https://arth.local/contracts/commands/patrons_add_household_member.schema.json', schema: patrons_add_household_memberSchema },
  { name: 'patrons_merge', id: 'https://arth.local/contracts/commands/patrons_merge.schema.json', schema: patrons_mergeSchema },
  { name: 'patrons_propose_merge', id: 'https://arth.local/contracts/commands/patrons_propose_merge.schema.json', schema: patrons_propose_mergeSchema },
  { name: 'patrons_update_command', id: 'https://arth.local/contracts/commands/patrons_update_command.schema.json', schema: patrons_update_commandSchema },
  { name: 'patrons_update_profile', id: 'https://arth.local/contracts/commands/patrons_update_profile.schema.json', schema: patrons_update_profileSchema },
  { name: 'payables_view', id: 'https://arth.local/contracts/payables_view.schema.json', schema: payables_viewSchema },
  { name: 'payment_daily_closed', id: 'https://arth.local/contracts/events/payment_daily_closed.schema.json', schema: payment_daily_closedSchema },
  { name: 'payment_exception_opened', id: 'https://arth.local/contracts/events/payment_exception_opened.schema.json', schema: payment_exception_openedSchema },
  { name: 'payment_exception_resolved', id: 'https://arth.local/contracts/events/payment_exception_resolved.schema.json', schema: payment_exception_resolvedSchema },
  { name: 'payment_expense_recorded', id: 'https://arth.local/contracts/events/payment_expense_recorded.schema.json', schema: payment_expense_recordedSchema },
  { name: 'payment_failed', id: 'https://arth.local/contracts/events/payment_failed.schema.json', schema: payment_failedSchema },
  { name: 'payment_matched', id: 'https://arth.local/contracts/events/payment_matched.schema.json', schema: payment_matchedSchema },
  { name: 'payment_pending', id: 'https://arth.local/contracts/events/payment_pending.schema.json', schema: payment_pendingSchema },
  { name: 'payment_received', id: 'https://arth.local/contracts/events/payment_received.schema.json', schema: payment_receivedSchema },
  { name: 'payment_refunded', id: 'https://arth.local/contracts/events/payment_refunded.schema.json', schema: payment_refundedSchema },
  { name: 'po_changed', id: 'https://arth.local/contracts/events/po_changed.schema.json', schema: po_changedSchema },
  { name: 'po_supplier_added', id: 'https://arth.local/contracts/events/po_supplier_added.schema.json', schema: po_supplier_addedSchema },
  { name: 'po_variance_found', id: 'https://arth.local/contracts/events/po_variance_found.schema.json', schema: po_variance_foundSchema },
  { name: 'po_view', id: 'https://arth.local/contracts/po_view.schema.json', schema: po_viewSchema },
  { name: 'privacy_erase_patron', id: 'https://arth.local/contracts/commands/privacy_erase_patron.schema.json', schema: privacy_erase_patronSchema },
  { name: 'privacy_erased', id: 'https://arth.local/contracts/events/privacy_erased.schema.json', schema: privacy_erasedSchema },
  { name: 'privacy_export_patron', id: 'https://arth.local/contracts/commands/privacy_export_patron.schema.json', schema: privacy_export_patronSchema },
  { name: 'privacy_exported', id: 'https://arth.local/contracts/events/privacy_exported.schema.json', schema: privacy_exportedSchema },
  { name: 'privacy_set_data_sharing', id: 'https://arth.local/contracts/commands/privacy_set_data_sharing.schema.json', schema: privacy_set_data_sharingSchema },
  { name: 'privacy_sharing_changed', id: 'https://arth.local/contracts/events/privacy_sharing_changed.schema.json', schema: privacy_sharing_changedSchema },
  { name: 'problem', id: 'https://arth.local/contracts/problem.schema.json', schema: problemSchema },
  { name: 'promises_view', id: 'https://arth.local/contracts/promises_view.schema.json', schema: promises_viewSchema },
  { name: 'public_storefront', id: 'https://arth.local/contracts/public_storefront.schema.json', schema: public_storefrontSchema },
  { name: 'reports_view', id: 'https://arth.local/contracts/reports_view.schema.json', schema: reports_viewSchema },
  { name: 'resolution_view', id: 'https://arth.local/contracts/resolution_view.schema.json', schema: resolution_viewSchema },
  { name: 'rewards_configure', id: 'https://arth.local/contracts/commands/rewards_configure.schema.json', schema: rewards_configureSchema },
  { name: 'rewards_record_visit', id: 'https://arth.local/contracts/commands/rewards_record_visit.schema.json', schema: rewards_record_visitSchema },
  { name: 'rewards_redeem', id: 'https://arth.local/contracts/commands/rewards_redeem.schema.json', schema: rewards_redeemSchema },
  { name: 'rx_view', id: 'https://arth.local/contracts/rx_view.schema.json', schema: rx_viewSchema },
  { name: 'sentinel_check', id: 'https://arth.local/contracts/commands/sentinel_check.schema.json', schema: sentinel_checkSchema },
  { name: 'sentinel_verdict', id: 'https://arth.local/contracts/events/sentinel_verdict.schema.json', schema: sentinel_verdictSchema },
  { name: 'session_result', id: 'https://arth.local/contracts/session_result.schema.json', schema: session_resultSchema },
  { name: 'settings_view', id: 'https://arth.local/contracts/settings_view.schema.json', schema: settings_viewSchema },
  { name: 'settlement_recorded', id: 'https://arth.local/contracts/events/settlement_recorded.schema.json', schema: settlement_recordedSchema },
  { name: 'shift_close', id: 'https://arth.local/contracts/commands/shift_close.schema.json', schema: shift_closeSchema },
  { name: 'shift_open', id: 'https://arth.local/contracts/commands/shift_open.schema.json', schema: shift_openSchema },
  { name: 'shift_view', id: 'https://arth.local/contracts/shift_view.schema.json', schema: shift_viewSchema },
  { name: 'staff_add', id: 'https://arth.local/contracts/commands/staff_add.schema.json', schema: staff_addSchema },
  { name: 'staff_add_command', id: 'https://arth.local/contracts/commands/staff_add_command.schema.json', schema: staff_add_commandSchema },
  { name: 'staff_added', id: 'https://arth.local/contracts/events/staff_added.schema.json', schema: staff_addedSchema },
  { name: 'staff_logged_in', id: 'https://arth.local/contracts/events/staff_logged_in.schema.json', schema: staff_logged_inSchema },
  { name: 'staff_login', id: 'https://arth.local/contracts/commands/staff_login.schema.json', schema: staff_loginSchema },
  { name: 'staff_login_command', id: 'https://arth.local/contracts/commands/staff_login_command.schema.json', schema: staff_login_commandSchema },
  { name: 'staff_logout', id: 'https://arth.local/contracts/commands/staff_logout.schema.json', schema: staff_logoutSchema },
  { name: 'staff_set_skills', id: 'https://arth.local/contracts/commands/staff_set_skills.schema.json', schema: staff_set_skillsSchema },
  { name: 'staff_shift_closed', id: 'https://arth.local/contracts/events/staff_shift_closed.schema.json', schema: staff_shift_closedSchema },
  { name: 'staff_shift_opened', id: 'https://arth.local/contracts/events/staff_shift_opened.schema.json', schema: staff_shift_openedSchema },
  { name: 'staff_skills_set', id: 'https://arth.local/contracts/events/staff_skills_set.schema.json', schema: staff_skills_setSchema },
  { name: 'staff_view', id: 'https://arth.local/contracts/staff_view.schema.json', schema: staff_viewSchema },
  { name: 'stock_adjust', id: 'https://arth.local/contracts/commands/stock_adjust.schema.json', schema: stock_adjustSchema },
  { name: 'stock_changed', id: 'https://arth.local/contracts/events/stock_changed.schema.json', schema: stock_changedSchema },
  { name: 'stock_count', id: 'https://arth.local/contracts/commands/stock_count.schema.json', schema: stock_countSchema },
  { name: 'stock_demand_logged', id: 'https://arth.local/contracts/events/stock_demand_logged.schema.json', schema: stock_demand_loggedSchema },
  { name: 'stock_log_unmet_demand', id: 'https://arth.local/contracts/commands/stock_log_unmet_demand.schema.json', schema: stock_log_unmet_demandSchema },
  { name: 'stock_override_recorded', id: 'https://arth.local/contracts/events/stock_override_recorded.schema.json', schema: stock_override_recordedSchema },
  { name: 'stock_recall_batch', id: 'https://arth.local/contracts/commands/stock_recall_batch.schema.json', schema: stock_recall_batchSchema },
  { name: 'stock_receive', id: 'https://arth.local/contracts/commands/stock_receive.schema.json', schema: stock_receiveSchema },
  { name: 'stock_view', id: 'https://arth.local/contracts/stock_view.schema.json', schema: stock_viewSchema },
  { name: 'storefront_publish', id: 'https://arth.local/contracts/commands/storefront_publish.schema.json', schema: storefront_publishSchema },
  { name: 'storefront_published', id: 'https://arth.local/contracts/events/storefront_published.schema.json', schema: storefront_publishedSchema },
  { name: 'storefront_view', id: 'https://arth.local/contracts/storefront_view.schema.json', schema: storefront_viewSchema },
  { name: 'suppliers_view', id: 'https://arth.local/contracts/suppliers_view.schema.json', schema: suppliers_viewSchema },
  { name: 'supply_add_supplier', id: 'https://arth.local/contracts/commands/supply_add_supplier.schema.json', schema: supply_add_supplierSchema },
  { name: 'supply_cancel_po', id: 'https://arth.local/contracts/commands/supply_cancel_po.schema.json', schema: supply_cancel_poSchema },
  { name: 'supply_confirm_po', id: 'https://arth.local/contracts/commands/supply_confirm_po.schema.json', schema: supply_confirm_poSchema },
  { name: 'supply_draft_po', id: 'https://arth.local/contracts/commands/supply_draft_po.schema.json', schema: supply_draft_poSchema },
  { name: 'supply_place_po', id: 'https://arth.local/contracts/commands/supply_place_po.schema.json', schema: supply_place_poSchema },
  { name: 'supply_receive', id: 'https://arth.local/contracts/commands/supply_receive.schema.json', schema: supply_receiveSchema },
  { name: 'supply_record_bill', id: 'https://arth.local/contracts/commands/supply_record_bill.schema.json', schema: supply_record_billSchema },
  { name: 'supply_record_quote', id: 'https://arth.local/contracts/commands/supply_record_quote.schema.json', schema: supply_record_quoteSchema },
  { name: 'supply_send_claim', id: 'https://arth.local/contracts/commands/supply_send_claim.schema.json', schema: supply_send_claimSchema },
  { name: 'tax_invoice_issued', id: 'https://arth.local/contracts/events/tax_invoice_issued.schema.json', schema: tax_invoice_issuedSchema },
  { name: 'treasury_daily_close', id: 'https://arth.local/contracts/commands/treasury_daily_close.schema.json', schema: treasury_daily_closeSchema },
  { name: 'treasury_expense', id: 'https://arth.local/contracts/commands/treasury_expense.schema.json', schema: treasury_expenseSchema },
  { name: 'treasury_match_bill', id: 'https://arth.local/contracts/commands/treasury_match_bill.schema.json', schema: treasury_match_billSchema },
  { name: 'treasury_match_khata', id: 'https://arth.local/contracts/commands/treasury_match_khata.schema.json', schema: treasury_match_khataSchema },
  { name: 'treasury_rails_event', id: 'https://arth.local/contracts/commands/treasury_rails_event.schema.json', schema: treasury_rails_eventSchema },
  { name: 'treasury_record_settlement', id: 'https://arth.local/contracts/commands/treasury_record_settlement.schema.json', schema: treasury_record_settlementSchema },
  { name: 'treasury_refund', id: 'https://arth.local/contracts/commands/treasury_refund.schema.json', schema: treasury_refundSchema },
  { name: 'treasury_resolve_exception', id: 'https://arth.local/contracts/commands/treasury_resolve_exception.schema.json', schema: treasury_resolve_exceptionSchema },
  { name: 'trust_view', id: 'https://arth.local/contracts/trust_view.schema.json', schema: trust_viewSchema },
  { name: 'verdict_view', id: 'https://arth.local/contracts/verdict_view.schema.json', schema: verdict_viewSchema },
  { name: 'view_invalidate', id: 'https://arth.local/contracts/events/view_invalidate.schema.json', schema: view_invalidateSchema },
] as const;

export type SchemaName = (typeof SCHEMAS)[number]['name'];

/** The generated type for each contract name. */
export interface ContractTypes {
  appointments_assign: AppointmentsAssign;
  appointments_book: AppointmentsBook;
  appointments_transition: AppointmentsTransition;
  appointments_view: AppointmentsView;
  appointments_walk_in: AppointmentsWalkIn;
  approval: ApprovalRequest;
  approval_decided: ApprovalDecided;
  approval_requested: ApprovalRequested;
  audit_verification: AuditVerification;
  audit_verified: AuditVerified;
  batch_recalled: BatchRecalled;
  bill_changed: BillChanged;
  bill_paid: BillPaid;
  bill_paid_view: BillPaidView;
  bill_pay_view: BillPayView;
  bill_price_override: BillPriceOverride;
  bill_returned: BillReturned;
  bill_ticket_changed: BillTicketChanged;
  bill_view: BillView;
  books_close_month: BooksCloseMonth;
  books_month_closed: BooksMonthClosed;
  capital_applied: CapitalApplied;
  capital_apply: CapitalApply;
  capital_offer_received: CapitalOfferReceived;
  capital_record_offer: CapitalRecordOffer;
  capital_view: CapitalView;
  catalog_add_item: CatalogAddItem;
  catalog_bulk_price: CatalogBulkPrice;
  catalog_change_price: CatalogChangePrice;
  catalog_import_items: CatalogImportItems;
  catalog_item_added: CatalogItemAdded;
  catalog_item_view: CatalogItemView;
  catalog_price_changed: CatalogPriceChanged;
  catalog_search_view: CatalogSearchView;
  claim_view: ClaimView;
  command: CommandRequest;
  command_executed: CommandExecuted;
  command_result: CommandResult;
  common: Common;
  consent_grant: ConsentGrant;
  consent_stop: ConsentStop;
  consent_withdraw: ConsentWithdraw;
  counter_add_lines: CounterAddLines;
  counter_advance_ticket: CounterAdvanceTicket;
  counter_attach_patron: CounterAttachPatron;
  counter_checkout: CounterCheckout;
  counter_checkout_khata: CounterCheckoutKhata;
  counter_open_bill: CounterOpenBill;
  counter_park: CounterPark;
  counter_remove_line: CounterRemoveLine;
  counter_request_upi: CounterRequestUpi;
  counter_resume: CounterResume;
  counter_return: CounterReturn;
  counter_send_to_kitchen: CounterSendToKitchen;
  counter_set_qty: CounterSetQty;
  counter_undo: CounterUndo;
  counter_void_bill: CounterVoidBill;
  credit_changed: CreditChanged;
  credit_payable_changed: CreditPayableChanged;
  credit_receipt_requested: CreditReceiptRequested;
  credit_reminder_requested: CreditReminderRequested;
  credit_statement_requested: CreditStatementRequested;
  customer_search_view: CustomerSearchView;
  demand_view: DemandView;
  device_health_reported: DeviceHealthReported;
  device_report_health: DeviceReportHealth;
  envelope: Envelope;
  event: DomainEvent;
  expiry_view: ExpiryView;
  feedback_record: FeedbackRecord;
  feedback_recorded: FeedbackRecorded;
  feedback_view: FeedbackView;
  gate_view: GateView;
  grn_view: GrnView;
  health_view: HealthView;
  hisaab_view: HisaabView;
  home_view: HomeView;
  i18n_changed: LanguageChanged;
  khata_account_view: KhataAccountView;
  khata_view: KhataView;
  kot_view: KotView;
  layer_pending_view: LayerPendingView;
  ledger_acknowledge_entry: LedgerAcknowledgeEntry;
  ledger_add_entry: LedgerAddEntry;
  ledger_add_payable: LedgerAddPayable;
  ledger_apply_advance: LedgerApplyAdvance;
  ledger_apply_verified_payment: LedgerApplyVerifiedPayment;
  ledger_dispute_entry: LedgerDisputeEntry;
  ledger_open_account: LedgerOpenAccount;
  ledger_pay_payable: LedgerPayPayable;
  ledger_record_deposit: LedgerRecordDeposit;
  ledger_record_payment: LedgerRecordPayment;
  ledger_record_promise: LedgerRecordPromise;
  ledger_resolve_dispute: LedgerResolveDispute;
  ledger_reverse_entry: LedgerReverseEntry;
  ledger_send_reminder: LedgerSendReminder;
  ledger_send_statement: LedgerSendStatement;
  ledger_set_limit: LedgerSetLimit;
  ledger_statement_view: LedgerStatementView;
  merchant_bootstrap: MerchantBootstrap;
  merchant_update_settings: MerchantUpdateSettings;
  notifications_view: NotificationsView;
  offer_cashback_requested: OfferCashbackRequested;
  offer_clawed_back: OfferClawedBack;
  offer_detail_view: OfferDetailView;
  offer_expired: OfferExpired;
  offer_issued: OfferIssued;
  offer_program_changed: OfferProgramChanged;
  offer_redeemed: OfferRedeemed;
  offers_create_program: OffersCreateProgram;
  offers_exclude_payers: OffersExcludePayers;
  offers_expire_due: OffersExpireDue;
  offers_pause_program: OffersPauseProgram;
  offers_view: OffersView;
  onboarding_complete_step: OnboardingCompleteStep;
  onboarding_started: OnboardingStarted;
  onboarding_updated: OnboardingUpdated;
  onboarding_view: OnboardingView;
  order_appointment_changed: OrderAppointmentChanged;
  order_changed: OrderChanged;
  order_view: OrderView;
  orders_accept: OrdersAccept;
  orders_advance: OrdersAdvance;
  orders_create_draft: OrdersCreateDraft;
  orders_decline: OrdersDecline;
  orders_place: OrdersPlace;
  orders_settle: OrdersSettle;
  orders_substitute: OrdersSubstitute;
  orders_view: OrdersView;
  park_view: ParkView;
  patron_changed: PatronChanged;
  patron_consent_changed: PatronConsentChanged;
  patron_export: PatronExport;
  patron_merged: PatronMerged;
  patron_reward_changed: PatronRewardChanged;
  patron_view: PatronView;
  patrons_add: PatronsAdd;
  patrons_add_command: PatronsAddCommand;
  patrons_add_household_member: PatronsAddHouseholdMember;
  patrons_merge: PatronsMerge;
  patrons_propose_merge: PatronsProposeMerge;
  patrons_update_command: PatronsUpdateCommand;
  patrons_update_profile: PatronsUpdateProfile;
  payables_view: PayablesView;
  payment_daily_closed: PaymentDailyClosed;
  payment_exception_opened: PaymentExceptionOpened;
  payment_exception_resolved: PaymentExceptionResolved;
  payment_expense_recorded: PaymentExpenseRecorded;
  payment_failed: PaymentFailed;
  payment_matched: PaymentMatched;
  payment_pending: PaymentPending;
  payment_received: PaymentReceived;
  payment_refunded: PaymentRefunded;
  po_changed: PoChanged;
  po_supplier_added: PoSupplierAdded;
  po_variance_found: PoVarianceFound;
  po_view: PoView;
  privacy_erase_patron: PrivacyErasePatron;
  privacy_erased: PrivacyErased;
  privacy_export_patron: PrivacyExportPatron;
  privacy_exported: PrivacyExported;
  privacy_set_data_sharing: PrivacySetDataSharing;
  privacy_sharing_changed: PrivacySharingChanged;
  problem: Problem;
  promises_view: PromisesView;
  public_storefront: PublicStorefront;
  reports_view: ReportsView;
  resolution_view: ResolutionView;
  rewards_configure: RewardsConfigure;
  rewards_record_visit: RewardsRecordVisit;
  rewards_redeem: RewardsRedeem;
  rx_view: RxView;
  sentinel_check: SentinelCheck;
  sentinel_verdict: SentinelVerdict;
  session_result: SessionResult;
  settings_view: SettingsView;
  settlement_recorded: SettlementRecorded;
  shift_close: ShiftClose;
  shift_open: ShiftOpen;
  shift_view: ShiftView;
  staff_add: StaffAdd;
  staff_add_command: StaffAddCommand;
  staff_added: StaffAdded;
  staff_logged_in: StaffLoggedIn;
  staff_login: StaffLogin;
  staff_login_command: StaffLoginCommand;
  staff_logout: StaffLogout;
  staff_set_skills: StaffSetSkills;
  staff_shift_closed: StaffShiftClosed;
  staff_shift_opened: StaffShiftOpened;
  staff_skills_set: StaffSkillsSet;
  staff_view: StaffView;
  stock_adjust: StockAdjust;
  stock_changed: StockChanged;
  stock_count: StockCount;
  stock_demand_logged: StockDemandLogged;
  stock_log_unmet_demand: StockLogUnmetDemand;
  stock_override_recorded: StockOverrideRecorded;
  stock_recall_batch: StockRecallBatch;
  stock_receive: StockReceive;
  stock_view: StockView;
  storefront_publish: StorefrontPublish;
  storefront_published: StorefrontPublished;
  storefront_view: StorefrontView;
  suppliers_view: SuppliersView;
  supply_add_supplier: SupplyAddSupplier;
  supply_cancel_po: SupplyCancelPo;
  supply_confirm_po: SupplyConfirmPo;
  supply_draft_po: SupplyDraftPo;
  supply_place_po: SupplyPlacePo;
  supply_receive: SupplyReceive;
  supply_record_bill: SupplyRecordBill;
  supply_record_quote: SupplyRecordQuote;
  supply_send_claim: SupplySendClaim;
  tax_invoice_issued: TaxInvoiceIssued;
  treasury_daily_close: TreasuryDailyClose;
  treasury_expense: TreasuryExpense;
  treasury_match_bill: TreasuryMatchBill;
  treasury_match_khata: TreasuryMatchKhata;
  treasury_rails_event: TreasuryRailsEvent;
  treasury_record_settlement: TreasuryRecordSettlement;
  treasury_refund: TreasuryRefund;
  treasury_resolve_exception: TreasuryResolveException;
  trust_view: TrustView;
  verdict_view: VerdictView;
  view_invalidate: ViewInvalidate;
}
