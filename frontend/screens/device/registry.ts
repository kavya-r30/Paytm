// Device screen registry: /device/<screen>/<param?> → component. Names match envelope `nav.screen` (C3).
import type { ComponentType } from 'react';
import * as Agents from './agents';
import * as Bill from './bill';
import type { ScreenProps } from './common';
import * as Entry from './entry';
import * as Grow from './grow';
import * as Growth from './growth';
import * as Khata from './khata';
import * as More from './more';
import * as Stock from './stock';
import * as Today from './today';

export const SCREENS: Record<string, ComponentType<ScreenProps>> = {
  home: Today.HomeScreen,
  ask: Today.AskScreen,
  forecast: Today.ForecastScreen,
  notifications: Today.NotificationsScreen,
  bill: Bill.BillScreen,
  pay: Bill.PayScreen,
  paid: Bill.PaidScreen,
  learn: Bill.LearnScreen,
  verdict: Bill.VerdictScreen,
  return: Bill.ReturnScreen,
  park: Bill.ParkScreen,
  orders: Bill.OrdersScreen,
  order: Bill.OrderScreen,
  khata: Khata.KhataScreen,
  patron: Khata.PatronScreen,
  promises: Khata.PromiseScreen,
  stock: Stock.StockScreen,
  item: Stock.ItemScreen,
  expiry: Stock.ExpiryScreen,
  suppliers: Stock.SuppliersScreen,
  po: Stock.PoScreen,
  gate: Stock.GateScreen,
  grn: Stock.GrnScreen,
  claim: Stock.ClaimScreen,
  grow: Growth.GrowScreen,
  plan: Growth.PlanScreen,
  demand: Grow.DemandScreen,
  bundle: Growth.BundleScreen,
  offers: Grow.OffersScreen,
  offer: Grow.OfferDetailScreen,
  campaign: Growth.CampaignScreen,
  ledger: Growth.LedgerScreen,
  storefront: Grow.StorefrontScreen,
  menu: More.MenuScreen,
  team: Agents.TeamScreen,
  run: Agents.RunScreen,
  memory: Agents.MemoryScreen,
  hisaab: More.HisaabScreen,
  reports: More.ReportsScreen,
  feedback: More.FeedbackScreen,
  language: More.LanguageScreen,
  staff: More.StaffScreen,
  trust: More.TrustScreen,
  health: More.HealthScreen,
  capital: More.CapitalScreen,
  onboarding: Entry.OnboardingScreen,
  pin: Entry.PinScreen,
  shift: Entry.ShiftScreen,
  kot: Entry.KotScreen,
  appointments: Entry.AppointmentsScreen,
  rx: Entry.RxScreen,
};

/** `bill/<id>/pay` and `bill/<id>/paid` are the J9 sub-routes of a bill. */
export function resolveScreen(segments: string[]): { Component: ComponentType<ScreenProps>; param?: string } {
  const [name = 'home', param, sub] = segments.map(decodeURIComponent);
  if (name === 'bill' && param && (sub === 'pay' || sub === 'paid'))
    return { Component: SCREENS[sub]!, param };
  return { Component: SCREENS[name] ?? Today.HomeScreen, param };
}
