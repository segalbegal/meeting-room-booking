from typing import Any
from uuid import UUID

import pytest

from meeting_room_booking.domain.room import Room
from tests.helpers import cases


@pytest.mark.parametrize("sample", cases("rooms_valid.json"))
def test_room_with_valid_data_is_created(sample: dict[str, Any]) -> None:
    room = Room(id=UUID(sample["id"]), name=sample["name"], capacity=sample["capacity"])
    assert room.id == UUID(sample["id"])
    assert room.name == sample["name"]
    assert room.capacity == sample["capacity"]


@pytest.mark.parametrize("sample", cases("rooms_invalid.json"))
def test_room_with_invalid_data_is_rejected(sample: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="positive"):
        Room(id=UUID(sample["id"]), name=sample["name"], capacity=sample["capacity"])
