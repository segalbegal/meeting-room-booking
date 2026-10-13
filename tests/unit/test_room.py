from uuid import uuid4

import pytest

from meeting_room_booking.domain.room import Room


def test_room_with_positive_capacity_is_created() -> None:
    room = Room(id=uuid4(), name="Fuji", capacity=2)
    assert room.name == "Fuji"
    assert room.capacity == 2


@pytest.mark.parametrize("capacity", [0, -1])
def test_room_with_non_positive_capacity_is_rejected(capacity: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        Room(id=uuid4(), name="Bad", capacity=capacity)
