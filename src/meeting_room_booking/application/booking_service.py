from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from meeting_room_booking.application.ports import BookingsRepository
from meeting_room_booking.domain.booking import Booking


@dataclass(frozen=True, slots=True)
class BookingsPage:
    bookings: list[Booking]
    total: int


async def list_room_bookings(
    repository: BookingsRepository,
    room_id: UUID,
    start: datetime | None,
    end: datetime | None,
    limit: int,
    offset: int,
) -> BookingsPage:
    bookings = sorted(
        await repository.get_active_for_room(room_id, start, end),
        key=lambda booking: booking.start,
    )
    return BookingsPage(bookings=bookings[offset : offset + limit], total=len(bookings))
