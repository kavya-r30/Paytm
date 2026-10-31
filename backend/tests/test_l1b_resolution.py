import json

from test_l1b_catalog import item, setup_catalog

from arth.core.paths import CONTRACTS_DIR, PACKS_DIR


async def test_150_utterance_deterministic_line(db):
    from arth.domains.catalog import read_starter
    from arth.domains.resolution import resolve
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    seeds = read_starter(PACKS_DIR / "kirana/catalog_starter.csv")
    await bus.submit(owner, "catalog.import_items", {"confirmed": True, "items": seeds}, "seed")
    cases = json.loads((CONTRACTS_DIR / "fixtures/catalog_resolution.json").read_text(encoding="utf-8"))
    assert len(cases) == 150
    correct = 0
    misses = []
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        for case in cases:
            result = await resolve(repo, case["query"])
            if result["selected"] and result["selected"]["sku"] == case["sku"]:
                correct += 1
            else:
                misses.append((case["query"], result))
    assert correct / 150 >= 0.92, misses


async def test_ambiguity_unknown_and_embedding_hook_are_scoped(db):
    from arth.domains.resolution import resolve
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    await bus.submit(owner, "catalog.add_item", item(), "one")
    await bus.submit(
        owner,
        "catalog.add_item",
        {**item(), "sku": "OTHER", "names": {"en": "Aashirvaad Salt"}, "barcodes": []},
        "two",
    )
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        result = await resolve(repo, "namak")
        assert result["needs_clarification"] and result["selected"] is None
        assert len(result["candidates"]) == 2
        assert (await resolve(repo, "wireless headphones"))["selected"] is None
        assert (await resolve(Repository(conn, "other"), "Tata Salt"))["candidates"] == []

        async def embeddings(query, candidates):
            return {"foreign_item": 1.0, candidates[0]["id"]: 0.95}

        result = await resolve(repo, "unknown semantic item", embedding_hook=embeddings)
        assert result["stage"] == "embedding" and result["selected"]["id"] != "foreign_item"
