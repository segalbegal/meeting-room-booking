from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import override
from uuid import UUID, uuid4

import pytest

from meeting_room_booking.domain.booking import Booking, BookingStatus
from meeting_room_booking.domain.clock import Clock
from meeting_room_booking.domain.room import Room

NOW = datetime(2030, 1, 1, 9, 0, tzinfo=UTC)


class FakeClock(Clock):
    def __init__(self, now: datetime = NOW) -> None:
        self._now = now

    @override
    def now(self) -> datetime:
        return self._now


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def room() -> Room:
    return Room(id=uuid4(), name="Everest", capacity=10)


BookingFactory = Callable[..., Booking]


@pytest.fixture
def make_booking() -> BookingFactory:
    def _make(
        *,
        room_id: UUID | None = None,
        start: datetime = NOW + timedelta(hours=1),
        duration: timedelta = timedelta(hours=1),
        status: BookingStatus = BookingStatus.active,
        title: str | None = "Sync",
        organizer_email: str = "organizer@example.com",
    ) -> Booking:
        return Booking(
            id=uuid4(),
            room_id=room_id or uuid4(),
            title=title,
            organizer_email=organizer_email,
            start=start,
            end=start + duration,
            status=status,
            created_at=NOW,
        )

    return _make
