import json
from pathlib import Path
from typing import Any

import pytest

from meeting_room_booking.domain import errors

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_json(filename: str) -> Any:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def cases(filename: str, key: str | None = None) -> list[Any]:
    """Load a JSON list of cases as pytest params, using each case's "case" field as its test id.

    If `key` is given, the file is an object and the list is read from that key.
    """
    data = load_json(filename)
    items = data[key] if key else data
    return [pytest.param(item, id=item["case"]) for item in items]


def domain_error(name: str | None) -> type[Exception] | None:
    """Resolve an error class name from a JSON case to the class in the domain errors module."""
    return None if name is None else getattr(errors, name)  # type: ignore[no-any-return]
