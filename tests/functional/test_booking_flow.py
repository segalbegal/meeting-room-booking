"""Functional: domain + service + repository wired together, no HTTP."""

from datetime import timedelta
from typing import Any
from uuid import uuid4

import pytest

from meeting_room_booking.application.booking_service import list_room_bookings
from meeting_room_booking.domain.booking import BookingStatus
from meeting_room_booking.domain.errors import InvalidBookingStartTimeError
from meeting_room_booking.infrastructure.in_memory import InMemoryBookingsRepository
from tests.conftest import NOW, BookingFactory, FakeClock
from tests.helpers import cases, load_json

TIME_FILTER = load_json("time_filter.json")


async def test_cancelled_bookings_disappear_from_listing(make_booking: BookingFactory) -> None:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    active = make_booking(room_id=room_id)
    cancelled = make_booking(room_id=room_id, start=NOW + timedelta(hours=3), status=BookingStatus.cancelled)
    await repo.add(active)
    await repo.add(cancelled)

    page = await list_room_bookings(repo, room_id, None, None, 50, 0)
    assert [b.id for b in page.bookings] == [active.id]


@pytest.mark.parametrize("sample", cases("time_filter.json", key="cases"))
async def test_time_window_filters_listing(make_booking: BookingFactory, sample: dict[str, Any]) -> None:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    for hours in TIME_FILTER["booking_start_hours"]:
        await repo.add(
            make_booking(
                room_id=room_id,
                start=NOW + timedelta(hours=hours),
                duration=timedelta(hours=TIME_FILTER["booking_duration_hours"]),
            )
        )

    start = None if sample["from_hours"] is None else NOW + timedelta(hours=sample["from_hours"])
    end = None if sample["to_hours"] is None else NOW + timedelta(hours=sample["to_hours"])
    page = await list_room_bookings(repo, room_id, start, end, 50, 0)
    assert page.total == sample["expected_total"]


async def test_booking_becomes_invalid_once_clock_passes_its_start(make_booking: BookingFactory) -> None:
    booking = make_booking(start=NOW + timedelta(hours=1))
    booking.validate_start_not_in_past(FakeClock(NOW))

    with pytest.raises(InvalidBookingStartTimeError):
        booking.validate_start_not_in_past(FakeClock(NOW + timedelta(days=1)))
