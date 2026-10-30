/* Generated from contracts. Do not edit; run `python dev.py gen`. */

import type { ApprovalRequest } from './approval';
import type { ApprovalDecided } from './approval_decided';
import type { ApprovalRequested } from './approval_requested';
import type { AuditVerification } from './audit_verification';
import type { AuditVerified } from './audit_verified';
import type { BatchRecalled } from './batch_recalled';
import type { CatalogAddItem } from './catalog_add_item';
import type { CatalogBulkPrice } from './catalog_bulk_price';
import type { CatalogChangePrice } from './catalog_change_price';
import type { CatalogImportItems } from './catalog_import_items';
import type { CatalogItemAdded } from './catalog_item_added';
import type { CatalogItemView } from './catalog_item_view';
import type { CatalogPriceChanged } from './catalog_price_changed';
import type { CatalogSearchView } from './catalog_search_view';
import type { CommandRequest } from './command';
import type { CommandExecuted } from './command_executed';
import type { CommandResult } from './command_result';
import type { Common } from './common';
import type { ConsentGrant } from './consent_grant';
import type { ConsentStop } from './consent_stop';
import type { ConsentWithdraw } from './consent_withdraw';
import type { CreditChanged } from './credit_changed';
import type { CreditPayableChanged } from './credit_payable_changed';
import type { CreditReceiptRequested } from './credit_receipt_requested';
import type { CreditReminderRequested } from './credit_reminder_requested';
import type { CreditStatementRequested } from './credit_statement_requested';
import type { CustomerSearchView } from './customer_search_view';
import type { Envelope } from './envelope';
import type { DomainEvent } from './event';
import type { ExpiryView } from './expiry_view';
import type { LanguageChanged } from './i18n_changed';
import type { KhataAccountView } from './khata_account_view';
import type { KhataView } from './khata_view';
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
import type { OnboardingCompleteStep } from './onboarding_complete_step';
import type { OnboardingStarted } from './onboarding_started';
import type { OnboardingUpdated } from './onboarding_updated';
import type { OnboardingView } from './onboarding_view';
import type { PatronChanged } from './patron_changed';
import type { PatronConsentChanged } from './patron_consent_changed';
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
import type { Problem } from './problem';
import type { PromisesView } from './promises_view';
import type { ResolutionView } from './resolution_view';
import type { RewardsConfigure } from './rewards_configure';
import type { RewardsRecordVisit } from './rewards_record_visit';
import type { RewardsRedeem } from './rewards_redeem';
import type { SessionResult } from './session_result';
import type { SettingsView } from './settings_view';
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
import type { StaffShiftClosed } from './staff_shift_closed';
import type { StaffShiftOpened } from './staff_shift_opened';
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
import type { ViewInvalidate } from './view_invalidate';
import approvalSchema from './schemas/approval.schema.json';
import approval_decidedSchema from './schemas/approval_decided.schema.json';
import approval_requestedSchema from './schemas/approval_requested.schema.json';
import audit_verificationSchema from './schemas/audit_verification.schema.json';
import audit_verifiedSchema from './schemas/audit_verified.schema.json';
import batch_recalledSchema from './schemas/batch_recalled.schema.json';
import catalog_add_itemSchema from './schemas/catalog_add_item.schema.json';
import catalog_bulk_priceSchema from './schemas/catalog_bulk_price.schema.json';
import catalog_change_priceSchema from './schemas/catalog_change_price.schema.json';
import catalog_import_itemsSchema from './schemas/catalog_import_items.schema.json';
import catalog_item_addedSchema from './schemas/catalog_item_added.schema.json';
import catalog_item_viewSchema from './schemas/catalog_item_view.schema.json';
import catalog_price_changedSchema from './schemas/catalog_price_changed.schema.json';
import catalog_search_viewSchema from './schemas/catalog_search_view.schema.json';
import commandSchema from './schemas/command.schema.json';
import command_executedSchema from './schemas/command_executed.schema.json';
import command_resultSchema from './schemas/command_result.schema.json';
import commonSchema from './schemas/common.schema.json';
import consent_grantSchema from './schemas/consent_grant.schema.json';
import consent_stopSchema from './schemas/consent_stop.schema.json';
import consent_withdrawSchema from './schemas/consent_withdraw.schema.json';
import credit_changedSchema from './schemas/credit_changed.schema.json';
import credit_payable_changedSchema from './schemas/credit_payable_changed.schema.json';
import credit_receipt_requestedSchema from './schemas/credit_receipt_requested.schema.json';
import credit_reminder_requestedSchema from './schemas/credit_reminder_requested.schema.json';
import credit_statement_requestedSchema from './schemas/credit_statement_requested.schema.json';
import customer_search_viewSchema from './schemas/customer_search_view.schema.json';
import envelopeSchema from './schemas/envelope.schema.json';
import eventSchema from './schemas/event.schema.json';
import expiry_viewSchema from './schemas/expiry_view.schema.json';
import i18n_changedSchema from './schemas/i18n_changed.schema.json';
import khata_account_viewSchema from './schemas/khata_account_view.schema.json';
import khata_viewSchema from './schemas/khata_view.schema.json';
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
import onboarding_complete_stepSchema from './schemas/onboarding_complete_step.schema.json';
import onboarding_startedSchema from './schemas/onboarding_started.schema.json';
import onboarding_updatedSchema from './schemas/onboarding_updated.schema.json';
import onboarding_viewSchema from './schemas/onboarding_view.schema.json';
import patron_changedSchema from './schemas/patron_changed.schema.json';
import patron_consent_changedSchema from './schemas/patron_consent_changed.schema.json';
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
import problemSchema from './schemas/problem.schema.json';
import promises_viewSchema from './schemas/promises_view.schema.json';
import resolution_viewSchema from './schemas/resolution_view.schema.json';
import rewards_configureSchema from './schemas/rewards_configure.schema.json';
import rewards_record_visitSchema from './schemas/rewards_record_visit.schema.json';
import rewards_redeemSchema from './schemas/rewards_redeem.schema.json';
import session_resultSchema from './schemas/session_result.schema.json';
import settings_viewSchema from './schemas/settings_view.schema.json';
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
import staff_shift_closedSchema from './schemas/staff_shift_closed.schema.json';
import staff_shift_openedSchema from './schemas/staff_shift_opened.schema.json';
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
import view_invalidateSchema from './schemas/view_invalidate.schema.json';

export type { ApprovalRequest } from './approval';
export type { ApprovalDecided } from './approval_decided';
export type { ApprovalRequested } from './approval_requested';
export type { AuditVerification } from './audit_verification';
export type { AuditVerified } from './audit_verified';
export type { BatchRecalled } from './batch_recalled';
export type { CatalogAddItem } from './catalog_add_item';
export type { CatalogBulkPrice } from './catalog_bulk_price';
export type { CatalogChangePrice } from './catalog_change_price';
export type { CatalogImportItems } from './catalog_import_items';
export type { CatalogItemAdded } from './catalog_item_added';
export type { CatalogItemView } from './catalog_item_view';
export type { CatalogPriceChanged } from './catalog_price_changed';
export type { CatalogSearchView } from './catalog_search_view';
export type { CommandRequest } from './command';
export type { CommandExecuted } from './command_executed';
export type { CommandResult } from './command_result';
export type { Common } from './common';
export type { ConsentGrant } from './consent_grant';
export type { ConsentStop } from './consent_stop';
export type { ConsentWithdraw } from './consent_withdraw';
export type { CreditChanged } from './credit_changed';
export type { CreditPayableChanged } from './credit_payable_changed';
export type { CreditReceiptRequested } from './credit_receipt_requested';
export type { CreditReminderRequested } from './credit_reminder_requested';
export type { CreditStatementRequested } from './credit_statement_requested';
export type { CustomerSearchView } from './customer_search_view';
export type { Envelope } from './envelope';
export type { DomainEvent } from './event';
export type { ExpiryView } from './expiry_view';
export type { LanguageChanged } from './i18n_changed';
export type { KhataAccountView } from './khata_account_view';
export type { KhataView } from './khata_view';
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
export type { OnboardingCompleteStep } from './onboarding_complete_step';
export type { OnboardingStarted } from './onboarding_started';
export type { OnboardingUpdated } from './onboarding_updated';
export type { OnboardingView } from './onboarding_view';
export type { PatronChanged } from './patron_changed';
export type { PatronConsentChanged } from './patron_consent_changed';
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
export type { Problem } from './problem';
export type { PromisesView } from './promises_view';
export type { ResolutionView } from './resolution_view';
export type { RewardsConfigure } from './rewards_configure';
export type { RewardsRecordVisit } from './rewards_record_visit';
export type { RewardsRedeem } from './rewards_redeem';
export type { SessionResult } from './session_result';
export type { SettingsView } from './settings_view';
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
export type { StaffShiftClosed } from './staff_shift_closed';
export type { StaffShiftOpened } from './staff_shift_opened';
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
export type { ViewInvalidate } from './view_invalidate';
export type * from './common'; // shared definitions: Locale, SpeechLocale, Audience, Tier, ...

/** Every contract: name (file stem), JSON Schema $id and the schema itself, for Ajv. */
export const SCHEMAS = [
  { name: 'approval', id: 'https://arth.local/contracts/approval.schema.json', schema: approvalSchema },
  { name: 'approval_decided', id: 'https://arth.local/contracts/events/approval_decided.schema.json', schema: approval_decidedSchema },
  { name: 'approval_requested', id: 'https://arth.local/contracts/events/approval_requested.schema.json', schema: approval_requestedSchema },
  { name: 'audit_verification', id: 'https://arth.local/contracts/audit_verification.schema.json', schema: audit_verificationSchema },
  { name: 'audit_verified', id: 'https://arth.local/contracts/events/audit_verified.schema.json', schema: audit_verifiedSchema },
  { name: 'batch_recalled', id: 'https://arth.local/contracts/events/batch_recalled.schema.json', schema: batch_recalledSchema },
  { name: 'catalog_add_item', id: 'https://arth.local/contracts/commands/catalog_add_item.schema.json', schema: catalog_add_itemSchema },
  { name: 'catalog_bulk_price', id: 'https://arth.local/contracts/commands/catalog_bulk_price.schema.json', schema: catalog_bulk_priceSchema },
  { name: 'catalog_change_price', id: 'https://arth.local/contracts/commands/catalog_change_price.schema.json', schema: catalog_change_priceSchema },
  { name: 'catalog_import_items', id: 'https://arth.local/contracts/commands/catalog_import_items.schema.json', schema: catalog_import_itemsSchema },
  { name: 'catalog_item_added', id: 'https://arth.local/contracts/events/catalog_item_added.schema.json', schema: catalog_item_addedSchema },
  { name: 'catalog_item_view', id: 'https://arth.local/contracts/catalog_item_view.schema.json', schema: catalog_item_viewSchema },
  { name: 'catalog_price_changed', id: 'https://arth.local/contracts/events/catalog_price_changed.schema.json', schema: catalog_price_changedSchema },
  { name: 'catalog_search_view', id: 'https://arth.local/contracts/catalog_search_view.schema.json', schema: catalog_search_viewSchema },
  { name: 'command', id: 'https://arth.local/contracts/command.schema.json', schema: commandSchema },
  { name: 'command_executed', id: 'https://arth.local/contracts/events/command_executed.schema.json', schema: command_executedSchema },
  { name: 'command_result', id: 'https://arth.local/contracts/command_result.schema.json', schema: command_resultSchema },
  { name: 'common', id: 'https://arth.local/contracts/common.schema.json', schema: commonSchema },
  { name: 'consent_grant', id: 'https://arth.local/contracts/commands/consent_grant.schema.json', schema: consent_grantSchema },
  { name: 'consent_stop', id: 'https://arth.local/contracts/commands/consent_stop.schema.json', schema: consent_stopSchema },
  { name: 'consent_withdraw', id: 'https://arth.local/contracts/commands/consent_withdraw.schema.json', schema: consent_withdrawSchema },
  { name: 'credit_changed', id: 'https://arth.local/contracts/events/credit_changed.schema.json', schema: credit_changedSchema },
  { name: 'credit_payable_changed', id: 'https://arth.local/contracts/events/credit_payable_changed.schema.json', schema: credit_payable_changedSchema },
  { name: 'credit_receipt_requested', id: 'https://arth.local/contracts/events/credit_receipt_requested.schema.json', schema: credit_receipt_requestedSchema },
  { name: 'credit_reminder_requested', id: 'https://arth.local/contracts/events/credit_reminder_requested.schema.json', schema: credit_reminder_requestedSchema },
  { name: 'credit_statement_requested', id: 'https://arth.local/contracts/events/credit_statement_requested.schema.json', schema: credit_statement_requestedSchema },
  { name: 'customer_search_view', id: 'https://arth.local/contracts/customer_search_view.schema.json', schema: customer_search_viewSchema },
  { name: 'envelope', id: 'https://arth.local/contracts/envelope.schema.json', schema: envelopeSchema },
  { name: 'event', id: 'https://arth.local/contracts/events/event.schema.json', schema: eventSchema },
  { name: 'expiry_view', id: 'https://arth.local/contracts/expiry_view.schema.json', schema: expiry_viewSchema },
  { name: 'i18n_changed', id: 'https://arth.local/contracts/events/i18n_changed.schema.json', schema: i18n_changedSchema },
  { name: 'khata_account_view', id: 'https://arth.local/contracts/khata_account_view.schema.json', schema: khata_account_viewSchema },
  { name: 'khata_view', id: 'https://arth.local/contracts/khata_view.schema.json', schema: khata_viewSchema },
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
  { name: 'onboarding_complete_step', id: 'https://arth.local/contracts/commands/onboarding_complete_step.schema.json', schema: onboarding_complete_stepSchema },
  { name: 'onboarding_started', id: 'https://arth.local/contracts/events/onboarding_started.schema.json', schema: onboarding_startedSchema },
  { name: 'onboarding_updated', id: 'https://arth.local/contracts/events/onboarding_updated.schema.json', schema: onboarding_updatedSchema },
  { name: 'onboarding_view', id: 'https://arth.local/contracts/onboarding_view.schema.json', schema: onboarding_viewSchema },
  { name: 'patron_changed', id: 'https://arth.local/contracts/events/patron_changed.schema.json', schema: patron_changedSchema },
  { name: 'patron_consent_changed', id: 'https://arth.local/contracts/events/patron_consent_changed.schema.json', schema: patron_consent_changedSchema },
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
  { name: 'problem', id: 'https://arth.local/contracts/problem.schema.json', schema: problemSchema },
  { name: 'promises_view', id: 'https://arth.local/contracts/promises_view.schema.json', schema: promises_viewSchema },
  { name: 'resolution_view', id: 'https://arth.local/contracts/resolution_view.schema.json', schema: resolution_viewSchema },
  { name: 'rewards_configure', id: 'https://arth.local/contracts/commands/rewards_configure.schema.json', schema: rewards_configureSchema },
  { name: 'rewards_record_visit', id: 'https://arth.local/contracts/commands/rewards_record_visit.schema.json', schema: rewards_record_visitSchema },
  { name: 'rewards_redeem', id: 'https://arth.local/contracts/commands/rewards_redeem.schema.json', schema: rewards_redeemSchema },
  { name: 'session_result', id: 'https://arth.local/contracts/session_result.schema.json', schema: session_resultSchema },
  { name: 'settings_view', id: 'https://arth.local/contracts/settings_view.schema.json', schema: settings_viewSchema },
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
  { name: 'staff_shift_closed', id: 'https://arth.local/contracts/events/staff_shift_closed.schema.json', schema: staff_shift_closedSchema },
  { name: 'staff_shift_opened', id: 'https://arth.local/contracts/events/staff_shift_opened.schema.json', schema: staff_shift_openedSchema },
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
  { name: 'view_invalidate', id: 'https://arth.local/contracts/events/view_invalidate.schema.json', schema: view_invalidateSchema },
] as const;

export type SchemaName = (typeof SCHEMAS)[number]['name'];

/** The generated type for each contract name. */
export interface ContractTypes {
  approval: ApprovalRequest;
  approval_decided: ApprovalDecided;
  approval_requested: ApprovalRequested;
  audit_verification: AuditVerification;
  audit_verified: AuditVerified;
  batch_recalled: BatchRecalled;
  catalog_add_item: CatalogAddItem;
  catalog_bulk_price: CatalogBulkPrice;
  catalog_change_price: CatalogChangePrice;
  catalog_import_items: CatalogImportItems;
  catalog_item_added: CatalogItemAdded;
  catalog_item_view: CatalogItemView;
  catalog_price_changed: CatalogPriceChanged;
  catalog_search_view: CatalogSearchView;
  command: CommandRequest;
  command_executed: CommandExecuted;
  command_result: CommandResult;
  common: Common;
  consent_grant: ConsentGrant;
  consent_stop: ConsentStop;
  consent_withdraw: ConsentWithdraw;
  credit_changed: CreditChanged;
  credit_payable_changed: CreditPayableChanged;
  credit_receipt_requested: CreditReceiptRequested;
  credit_reminder_requested: CreditReminderRequested;
  credit_statement_requested: CreditStatementRequested;
  customer_search_view: CustomerSearchView;
  envelope: Envelope;
  event: DomainEvent;
  expiry_view: ExpiryView;
  i18n_changed: LanguageChanged;
  khata_account_view: KhataAccountView;
  khata_view: KhataView;
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
  onboarding_complete_step: OnboardingCompleteStep;
  onboarding_started: OnboardingStarted;
  onboarding_updated: OnboardingUpdated;
  onboarding_view: OnboardingView;
  patron_changed: PatronChanged;
  patron_consent_changed: PatronConsentChanged;
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
  problem: Problem;
  promises_view: PromisesView;
  resolution_view: ResolutionView;
  rewards_configure: RewardsConfigure;
  rewards_record_visit: RewardsRecordVisit;
  rewards_redeem: RewardsRedeem;
  session_result: SessionResult;
  settings_view: SettingsView;
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
  staff_shift_closed: StaffShiftClosed;
  staff_shift_opened: StaffShiftOpened;
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
  view_invalidate: ViewInvalidate;
}
