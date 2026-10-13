from datetime import timedelta
from typing import Any
from uuid import uuid4

import httpx
import pytest

from meeting_room_booking.domain.booking import BookingStatus
from meeting_room_booking.domain.room import Room
from meeting_room_booking.infrastructure.in_memory import (
    InMemoryBookingsRepository,
    InMemoryRoomsRepository,
)
from tests.conftest import NOW, BookingFactory


async def test_get_booking_returns_booking(
    async_client: httpx.AsyncClient, bookings_repo: InMemoryBookingsRepository, make_booking: BookingFactory
) -> None:
    booking = make_booking(title=None)
    await bookings_repo.add(booking)

    response = await async_client.get(f"/bookings/{booking.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(booking.id)
    assert body["room_id"] == str(booking.room_id)
    assert body["title"] is None
    assert body["organizer_email"] == booking.organizer_email
    assert body["status"] == "active"


async def test_get_cancelled_booking_is_still_retrievable(
    async_client: httpx.AsyncClient, bookings_repo: InMemoryBookingsRepository, make_booking: BookingFactory
) -> None:
    booking = make_booking(status=BookingStatus.cancelled)
    await bookings_repo.add(booking)
    response = await async_client.get(f"/bookings/{booking.id}")
    assert response.json()["status"] == "cancelled"


async def test_get_unknown_booking_is_404(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get(f"/bookings/{uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


async def test_get_booking_with_invalid_id_is_422(async_client: httpx.AsyncClient) -> None:
    assert (await async_client.get("/bookings/123")).status_code == 422


@pytest.fixture
async def seeded_room(rooms_repo: InMemoryRoomsRepository, room: Room) -> Room:
    await rooms_repo.add(room)
    return room


async def _seed(repo: InMemoryBookingsRepository, make_booking: BookingFactory, room: Room, n: int) -> None:
    for i in range(n):
        await repo.add(make_booking(room_id=room.id, start=NOW + timedelta(hours=2 * i + 1)))


async def test_list_room_bookings_sorted_and_excludes_cancelled(
    async_client: httpx.AsyncClient,
    bookings_repo: InMemoryBookingsRepository,
    make_booking: BookingFactory,
    seeded_room: Room,
) -> None:
    await _seed(bookings_repo, make_booking, seeded_room, 3)
    await bookings_repo.add(make_booking(room_id=seeded_room.id, status=BookingStatus.cancelled))
    await bookings_repo.add(make_booking(room_id=uuid4()))

    body = (await async_client.get(f"/rooms/{seeded_room.id}/bookings")).json()

    assert body["total"] == 3
    starts = [b["start"] for b in body["bookings"]]
    assert starts == sorted(starts)


async def test_list_room_bookings_pagination(
    async_client: httpx.AsyncClient,
    bookings_repo: InMemoryBookingsRepository,
    make_booking: BookingFactory,
    seeded_room: Room,
) -> None:
    await _seed(bookings_repo, make_booking, seeded_room, 5)
    response = await async_client.get(f"/rooms/{seeded_room.id}/bookings", params={"limit": 2, "offset": 4})
    body = response.json()
    assert (body["total"], body["limit"], body["offset"], len(body["bookings"])) == (5, 2, 4, 1)


async def test_list_room_bookings_time_filter(
    async_client: httpx.AsyncClient,
    bookings_repo: InMemoryBookingsRepository,
    make_booking: BookingFactory,
    seeded_room: Room,
) -> None:
    await _seed(bookings_repo, make_booking, seeded_room, 3)  # 1h long, starting +1h, +3h, +5h
    params = {"from": (NOW + timedelta(hours=2)).isoformat(), "to": (NOW + timedelta(hours=4)).isoformat()}
    response = await async_client.get(f"/rooms/{seeded_room.id}/bookings", params=params)
    assert response.json()["total"] == 1


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
        {"from": "2030-01-01T10:00:00"},  # naive datetime; AwareDatetime required
        {"to": "garbage"},
    ],
)
async def test_list_room_bookings_invalid_query_is_422(
    async_client: httpx.AsyncClient, seeded_room: Room, params: dict[str, Any]
) -> None:
    response = await async_client.get(f"/rooms/{seeded_room.id}/bookings", params=params)
    assert response.status_code == 422
