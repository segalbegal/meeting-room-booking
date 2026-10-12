from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from meeting_room_booking.domain.booking import Booking
from meeting_room_booking.domain.room import Room


class RoomsRepository(ABC):
    @abstractmethod
    async def add(self, room: Room) -> None: ...

    @abstractmethod
    async def get_by_id(self, room_id: UUID) -> Room | None: ...

    @abstractmethod
    async def get_all(self) -> list[Room]: ...


class BookingsRepository(ABC):
    @abstractmethod
    async def add(self, booking: Booking) -> None: ...

    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Booking | None: ...

    @abstractmethod
    async def get_active_for_room(
        self, room_id: UUID, start: datetime | None, end: datetime | None
    ) -> list[Booking]:
        """Active bookings of the room overlapping [start, end); open-ended if a bound is None."""


class RoomsSource(ABC):
    @abstractmethod
    async def load(self) -> list[Room]: ...
