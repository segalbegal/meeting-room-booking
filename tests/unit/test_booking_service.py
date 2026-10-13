from datetime import timedelta
from typing import Any
from uuid import uuid4

import pytest

from meeting_room_booking.application.booking_service import list_room_bookings
from meeting_room_booking.infrastructure.in_memory import InMemoryBookingsRepository
from tests.conftest import NOW, BookingFactory
from tests.helpers import cases


async def _seed(make_booking: BookingFactory, count: int) -> tuple[InMemoryBookingsRepository, Any]:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    # inserted in reverse so sorting is actually exercised
    for i in reversed(range(count)):
        await repo.add(make_booking(room_id=room_id, start=NOW + timedelta(hours=i + 1)))
    return repo, room_id


async def test_bookings_are_sorted_by_start(make_booking: BookingFactory) -> None:
    repo, room_id = await _seed(make_booking, 3)
    page = await list_room_bookings(repo, room_id, None, None, limit=10, offset=0)
    starts = [b.start for b in page.bookings]
    assert starts == sorted(starts)


@pytest.mark.parametrize("sample", cases("pagination.json"))
async def test_pagination(make_booking: BookingFactory, sample: dict[str, Any]) -> None:
    repo, room_id = await _seed(make_booking, sample["total"])
    page = await list_room_bookings(repo, room_id, None, None, sample["limit"], sample["offset"])
    assert len(page.bookings) == sample["expected_len"]
    assert page.total == sample["total"]
