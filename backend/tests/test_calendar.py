from datetime import date
from pathlib import Path

import pytest

from arth.core.calendar import CalendarIndex, Occurrence, load_calendar
from arth.core.config import ConfigError
from arth.core.paths import CONFIG_DIR

DEMO_DAY = date(2026, 10, 29)


@pytest.fixture(scope="module")
def repo() -> CalendarIndex:
    return CalendarIndex(load_calendar(CONFIG_DIR / "calendar"))


def kinds(index: CalendarIndex, city: str, start: date, end: date) -> set[str]:
    return {o.kind for o in index.between(city, start, end)}


# ---- Demo-scenario invariants (gupta_diwali, Lucknow) -----------------------------------------
# These pin real repo data used by the demo; if one fails, fix the calendar YAML row (cite its source).


def test_lucknow_sees_karva_chauth_on_demo_day_and_chennai_does_not(repo: CalendarIndex) -> None:
    assert "karva_chauth" in kinds(repo, "lucknow", DEMO_DAY, DEMO_DAY)
    assert "karva_chauth" not in kinds(repo, "chennai", DEMO_DAY, DEMO_DAY)


def test_chennai_sees_pongal_and_lucknow_does_not(repo: CalendarIndex) -> None:
    jan = (date(2026, 1, 13), date(2026, 1, 17))
    assert "pongal" in kinds(repo, "chennai", *jan)
    assert "pongal" not in kinds(repo, "lucknow", *jan)


def test_kolkata_durga_puja_and_varanasi_dev_deepawali(repo: CalendarIndex) -> None:
    assert "durga_puja" in kinds(repo, "kolkata", date(2026, 10, 17), date(2026, 10, 20))
    assert "dev_deepawali" in kinds(repo, "varanasi", date(2026, 11, 24), date(2026, 11, 24))
    assert "dev_deepawali" not in kinds(repo, "lucknow", date(2026, 11, 24), date(2026, 11, 24))


def test_diwali_is_ten_days_from_demo_start_in_lucknow(repo: CalendarIndex) -> None:
    assert repo.days_until("diwali", DEMO_DAY, city="lucknow") == 10


def test_lucknow_demo_window_has_the_whole_festive_run(repo: CalendarIndex) -> None:
    window = kinds(repo, "lucknow", DEMO_DAY, date(2026, 11, 30))
    assert {
        "karva_chauth",
        "dhanteras",
        "diwali",
        "govardhan_puja",
        "bhai_dooj",
        "chhath",
        "guru_nanak_jayanti",
    } <= window


def test_last_years_diwali_is_available_for_comparison(repo: CalendarIndex) -> None:
    assert "diwali" in kinds(repo, "lucknow", date(2025, 10, 20), date(2025, 10, 20))


def test_salary_week_recurs_monthly(repo: CalendarIndex) -> None:
    salary = [
        o for o in repo.between("lucknow", date(2026, 11, 1), date(2026, 11, 30)) if o.kind == "salary_days"
    ]
    assert [o.start.day for o in salary] == [1, 2, 3, 4, 5, 6, 7]


# ---- Repo-wide invariants ----------------------------------------------------------------------


def test_every_event_has_source_and_confidence(repo: CalendarIndex) -> None:
    for occurrence in repo.between("lucknow", date(2025, 8, 1), date(2027, 12, 31)):
        assert occurrence.confidence and occurrence.source


def test_unknown_city_is_a_clear_error(repo: CalendarIndex) -> None:
    with pytest.raises(ConfigError, match="regions.yaml"):
        repo.between("atlantis", DEMO_DAY, DEMO_DAY)


# ---- Fixture calendars -------------------------------------------------------------------------

REGIONS = (
    "states:\n"
    "  - { code: IN-UP, name: Uttar Pradesh, ui_locale: hi, cities: [lucknow] }\n"
    "  - { code: IN-TN, name: Tamil Nadu, ui_locale: ta, cities: [chennai] }\n"
)


def fixture_calendar(tmp_path: Path, events_yaml: str, regions: str = REGIONS) -> Path:
    folder = tmp_path / "calendar"
    folder.mkdir()
    (folder / "regions.yaml").write_text(regions, encoding="utf-8")
    (folder / "events-test.yaml").write_text(events_yaml, encoding="utf-8")
    return folder


EVENT = """events:
  - id: fest_2026
    kind: fest
    type: festival
    names: {{ en: Fest }}
    start: 2026-11-08
    {extra}
    confidence: regional_variant
    source: test
"""

RECURRING = """recurring:
  - id: rec
    kind: rec
    names: {{ en: Rec }}
    rule: monthly_days
    days: {days}
    scope: {{ national: true }}
    source: test
"""


def build(tmp_path: Path, yaml_text: str) -> CalendarIndex:
    return CalendarIndex(load_calendar(fixture_calendar(tmp_path, yaml_text)))


def test_state_override_moves_the_date_for_that_state_only(tmp_path: Path) -> None:
    index = build(
        tmp_path, EVENT.format(extra="scope: { national: true }\n    date_overrides: { IN-TN: 2026-11-07 }")
    )
    assert index.days_until("fest", DEMO_DAY, city="lucknow") == 10
    assert index.days_until("fest", DEMO_DAY, city="chennai") == 9


def test_multi_day_event_counts_while_ongoing(tmp_path: Path) -> None:
    index = build(tmp_path, EVENT.format(extra="end: 2026-11-12\n    scope: { national: true }"))
    assert [o.kind for o in index.upcoming("lucknow", date(2026, 11, 10), within_days=0)] == ["fest"]


def test_unknown_place_fails_at_boot_and_names_the_file(tmp_path: Path) -> None:
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: { states: [IN-XX] }"))
    with pytest.raises(ConfigError, match=r"events-test\.yaml.*IN-XX"):
        CalendarIndex(load_calendar(folder))


def test_empty_scope_is_rejected(tmp_path: Path) -> None:
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: {}"))
    with pytest.raises(ConfigError, match="scope"):
        load_calendar(folder)


def test_occurrence_carries_event_fields(tmp_path: Path) -> None:
    index = build(
        tmp_path,
        EVENT.format(
            extra="scope: { national: true }\n    closure: partial\n    note: n1\n    lead_days: 5\n"
            "    tail_days: 2\n    priors: { sweets: { lift: 2.0 } }"
        ),
    )
    (occ,) = index.between("lucknow", date(2026, 11, 8), date(2026, 11, 8))
    assert (occ.type, occ.names, occ.closure, occ.note) == ("festival", {"en": "Fest"}, "partial", "n1")
    assert (occ.lead_days, occ.tail_days) == (5, 2)
    occ.priors["sweets"]["lift"] = 99.0  # must not leak back into the loaded calendar
    (again,) = index.between("lucknow", date(2026, 11, 8), date(2026, 11, 8))
    assert again.priors["sweets"]["lift"] == 2.0


def test_lead_and_tail_windows_are_not_applied_by_between(tmp_path: Path) -> None:
    index = build(
        tmp_path, EVENT.format(extra="scope: { national: true }\n    lead_days: 5\n    tail_days: 3")
    )
    assert index.between("lucknow", date(2026, 11, 1), date(2026, 11, 7)) == []
    assert index.between("lucknow", date(2026, 11, 9), date(2026, 11, 12)) == []


def test_recurring_defaults(tmp_path: Path) -> None:
    index = build(tmp_path, RECURRING.format(days="[5]"))
    (occ,) = index.between("lucknow", date(2026, 11, 1), date(2026, 11, 30))
    assert isinstance(occ, Occurrence)
    assert (occ.type, occ.confidence, occ.closure, occ.names) == (
        "observance",
        "published",
        "none",
        {"en": "Rec"},
    )


def test_day_31_is_skipped_in_a_30_day_month(tmp_path: Path) -> None:
    index = build(tmp_path, RECURRING.format(days="[30, 31]"))
    nov = [o.start for o in index.between("lucknow", date(2026, 11, 1), date(2026, 11, 30))]
    assert nov == [date(2026, 11, 30)]
    dec = [o.start for o in index.between("lucknow", date(2026, 12, 1), date(2026, 12, 31))]
    assert dec == [date(2026, 12, 30), date(2026, 12, 31)]


def test_range_spanning_december_into_january(tmp_path: Path) -> None:
    index = build(tmp_path, RECURRING.format(days="[1, 28]"))
    found = [o.start for o in index.between("lucknow", date(2026, 12, 15), date(2027, 1, 15))]
    assert found == [date(2026, 12, 28), date(2027, 1, 1)]


@pytest.mark.parametrize("days", ["[]", "[0]", "[32]", "[-1]", "[3, 3]"])
def test_recurring_days_are_validated(tmp_path: Path, days: str) -> None:
    folder = fixture_calendar(tmp_path, RECURRING.format(days=days))
    with pytest.raises(ConfigError, match="days"):
        load_calendar(folder)


def test_days_until_raises_key_error_when_nothing_upcoming(tmp_path: Path) -> None:
    index = build(tmp_path, EVENT.format(extra="scope: { national: true }"))
    with pytest.raises(KeyError, match="nothing"):
        index.days_until("nothing", DEMO_DAY, city="lucknow")


def test_duplicate_ids_across_files_name_both_files(tmp_path: Path) -> None:
    body = EVENT.format(extra="scope: { national: true }")
    folder = fixture_calendar(tmp_path, body)
    (folder / "events-other.yaml").write_text(body, encoding="utf-8")
    with pytest.raises(ConfigError, match=r"events-test\.yaml.*fest_2026|fest_2026.*events-test\.yaml"):
        load_calendar(folder)


def test_duplicate_city_across_states_is_rejected(tmp_path: Path) -> None:
    regions = REGIONS + "  - { code: IN-MH, name: Maharashtra, ui_locale: mr, cities: [lucknow] }\n"
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: { national: true }"), regions=regions)
    with pytest.raises(ConfigError, match=r"(?s)regions\.yaml.*lucknow"):
        load_calendar(folder)


def test_stray_yaml_in_calendar_dir_is_rejected(tmp_path: Path) -> None:
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: { national: true }"))
    (folder / "event-2028.yaml").write_text("events: []\n", encoding="utf-8")
    with pytest.raises(ConfigError, match=r"event-2028\.yaml"):
        load_calendar(folder)


@pytest.mark.parametrize("field", ["source: ''", "names: { en: '' }"])
def test_blank_source_or_name_is_rejected(tmp_path: Path, field: str) -> None:
    text = EVENT.format(extra="scope: { national: true }")
    key = field.split(":")[0]
    text = "\n".join(line for line in text.splitlines() if not line.strip().startswith(key + ":"))
    text += f"    {field}\n"
    with pytest.raises(ConfigError, match="events-test.yaml"):
        load_calendar(fixture_calendar(tmp_path, text))
