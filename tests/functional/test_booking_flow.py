"""Functional: domain + service + repository wired together, no HTTP."""

from datetime import timedelta
from uuid import uuid4

import pytest

from meeting_room_booking.application.booking_service import list_room_bookings
from meeting_room_booking.domain.booking import BookingStatus
from meeting_room_booking.domain.errors import InvalidBookingStartTimeError
from meeting_room_booking.infrastructure.in_memory import InMemoryBookingsRepository
from tests.conftest import NOW, BookingFactory, FakeClock


async def test_cancelled_bookings_disappear_from_listing(make_booking: BookingFactory) -> None:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    active = make_booking(room_id=room_id)
    cancelled = make_booking(room_id=room_id, start=NOW + timedelta(hours=3), status=BookingStatus.cancelled)
    await repo.add(active)
    await repo.add(cancelled)

    page = await list_room_bookings(repo, room_id, None, None, 50, 0)
    assert [b.id for b in page.bookings] == [active.id]


async def test_time_window_filters_listing(make_booking: BookingFactory) -> None:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    early = make_booking(room_id=room_id, start=NOW + timedelta(hours=1))
    late = make_booking(room_id=room_id, start=NOW + timedelta(hours=10))
    await repo.add(early)
    await repo.add(late)

    page = await list_room_bookings(repo, room_id, NOW + timedelta(hours=5), None, 50, 0)
    assert [b.id for b in page.bookings] == [late.id]


async def test_booking_becomes_invalid_once_clock_passes_its_start(make_booking: BookingFactory) -> None:
    booking = make_booking(start=NOW + timedelta(hours=1))
    clock = FakeClock(NOW)
    booking.validate_start_not_in_past(clock)

    clock = FakeClock(NOW + timedelta(days=1))
    with pytest.raises(InvalidBookingStartTimeError):
        booking.validate_start_not_in_past(clock)
