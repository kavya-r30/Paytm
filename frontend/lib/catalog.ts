// `catalog.add_item` payloads built from what the owner entered or what Arth found (Learn, demand capture,
// bundles). The contract needs a SKU, category and cost; a new item gets a generated SKU, and a cost the
// owner did not give is left equal to the price (zero margin), so margin reports never overstate profit.

export type NewItem = {
  name: string;
  pricePaise: number;
  mrpPaise?: number;
  costPaise?: number;
  unit?: string;
  category?: string;
  recipe?: { item_id: string; qty_milli: number }[];
  details?: Record<string, unknown>;
};

export function newSku(name: string): string {
  const slug = name
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 24);
  return `${slug || 'ITEM'}-${Date.now().toString(36).toUpperCase()}`;
}

export function addItemPayload(item: NewItem): Record<string, unknown> {
  return {
    sku: newSku(item.name),
    names: { en: item.name.trim() },
    unit: item.unit ?? 'pcs',
    mrp_paise: item.mrpPaise ?? item.pricePaise,
    price_paise: item.pricePaise,
    cost_paise: item.costPaise ?? item.pricePaise,
    category: item.category ?? 'general',
    ...(item.recipe?.length ? { recipe: item.recipe } : {}),
    ...(item.details ? { details: item.details } : {}),
  };
}
