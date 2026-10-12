from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from meeting_room_booking.api.routers import bookings, rooms
from meeting_room_booking.application.ports import BookingsRepository, RoomsRepository, RoomsSource
from meeting_room_booking.application.room_seeding import seed_rooms
from meeting_room_booking.domain.clock import Clock
from meeting_room_booking.infrastructure.in_memory import (
    InMemoryBookingsRepository,
    InMemoryRoomsRepository,
)
from meeting_room_booking.infrastructure.json_rooms_source import JsonFileRoomsSource
from meeting_room_booking.infrastructure.system_clock import SystemClock

DEFAULT_ROOMS_FILE = Path(__file__).resolve().parents[2] / "data" / "rooms.json"


def create_app(
    rooms_repository: RoomsRepository | None = None,
    bookings_repository: BookingsRepository | None = None,
    clock: Clock | None = None,
    rooms_source: RoomsSource | None = None,
) -> FastAPI:
    source = rooms_source or JsonFileRoomsSource(DEFAULT_ROOMS_FILE)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        await seed_rooms(source, app.state.rooms_repository)
        yield

    app = FastAPI(title="Meeting Room Booking", lifespan=lifespan)

    app.state.rooms_repository = rooms_repository or InMemoryRoomsRepository()
    app.state.bookings_repository = bookings_repository or InMemoryBookingsRepository()

    app.state.clock = clock or SystemClock()

    app.include_router(rooms.router)
    app.include_router(bookings.router)

    return app
