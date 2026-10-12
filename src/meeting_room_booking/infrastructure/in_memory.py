from datetime import datetime
from typing import override
from uuid import UUID

from meeting_room_booking.application.ports import BookingsRepository, RoomsRepository
from meeting_room_booking.domain.booking import Booking, BookingStatus
from meeting_room_booking.domain.room import Room


class InMemoryRoomsRepository(RoomsRepository):
    def __init__(self) -> None:
        self._rooms: dict[UUID, Room] = {}

    @override
    async def add(self, room: Room) -> None:
        self._rooms[room.id] = room

    @override
    async def get_by_id(self, room_id: UUID) -> Room | None:
        return self._rooms.get(room_id)

    @override
    async def get_all(self) -> list[Room]:
        return list(self._rooms.values())


class InMemoryBookingsRepository(BookingsRepository):
    def __init__(self) -> None:
        self._bookings: dict[UUID, Booking] = {}

    @override
    async def add(self, booking: Booking) -> None:
        self._bookings[booking.id] = booking

    @override
    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        return self._bookings.get(booking_id)

    @override
    async def get_active_for_room(
        self, room_id: UUID, start: datetime | None, end: datetime | None
    ) -> list[Booking]:
        return [
            booking
            for booking in self._bookings.values()
            if booking.room_id == room_id
            and booking.status == BookingStatus.active
            and (start is None or booking.end > start)
            and (end is None or booking.start < end)
        ]
