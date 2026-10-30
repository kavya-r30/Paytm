import pytest

from arth.core.ids import IdError, kind_of, new_id, parse_id


def test_new_id_has_kind_prefix_and_ulid() -> None:
    value = new_id("bill")
    kind, ulid = parse_id(value)
    assert kind == "bill"
    assert len(ulid) == 26
    assert kind_of(value) == "bill"


def test_ids_are_unique() -> None:
    assert len({new_id("pat") for _ in range(1000)}) == 1000


@pytest.mark.parametrize("kind", ["", "B", "bill-x", "x", "averyverylongkind", "bill\n"])
def test_rejects_bad_kind(kind: str) -> None:
    with pytest.raises(IdError):
        new_id(kind)


@pytest.mark.parametrize(
    "value",
    [
        "bill",
        "bill_123",
        "Bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
        "bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9TU",
        "bill\n_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
        "bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1\n",
        "bill_81JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
    ],
)
def test_rejects_bad_id(value: str) -> None:
    with pytest.raises(IdError):
        parse_id(value)
    with pytest.raises(IdError):
        kind_of(value)


def test_first_ulid_char_up_to_7_is_accepted() -> None:
    assert parse_id("bill_71JBQ0Z7Y8K3M4N5P6Q7R8S9T1")[0] == "bill"


def test_ids_generated_in_a_loop_have_non_decreasing_timestamps() -> None:
    # Millisecond-level monotonicity only: within one ms the random part is unordered.
    stamps = [new_id("pat").split("_")[1][:10] for _ in range(2000)]
    assert stamps == sorted(stamps)
