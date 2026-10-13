from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from meeting_room_booking.domain.room import Room
from meeting_room_booking.infrastructure.in_memory import (
    InMemoryBookingsRepository,
    InMemoryRoomsRepository,
)
from meeting_room_booking.main import create_app
from tests.conftest import FakeClock
from tests.functional.test_room_seeding import StaticSource


@pytest.fixture
def rooms_repo() -> InMemoryRoomsRepository:
    return InMemoryRoomsRepository()


@pytest.fixture
def bookings_repo() -> InMemoryBookingsRepository:
    return InMemoryBookingsRepository()


@pytest.fixture
def app(
    rooms_repo: InMemoryRoomsRepository,
    bookings_repo: InMemoryBookingsRepository,
    clock: FakeClock,
    room: Room,
) -> FastAPI:
    return create_app(
        rooms_repository=rooms_repo,
        bookings_repository=bookings_repo,
        clock=clock,
        rooms_source=StaticSource([room]),
    )


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """Runs the lifespan, so rooms are seeded from the static source."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """Lifespan is NOT run; tests seed repositories directly."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
