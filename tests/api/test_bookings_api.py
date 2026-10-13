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
from tests.helpers import cases, load_json

TIME_FILTER = load_json("time_filter.json")


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


@pytest.mark.parametrize("sample", cases("invalid_ids.json"))
async def test_get_booking_with_invalid_id_is_422(async_client: httpx.AsyncClient, sample: dict[str, Any]) -> None:
    assert (await async_client.get(f"/bookings/{sample['value']}")).status_code == 422


@pytest.fixture
async def seeded_room(rooms_repo: InMemoryRoomsRepository, room: Room) -> Room:
    await rooms_repo.add(room)
    return room


async def _seed(repo: InMemoryBookingsRepository, make_booking: BookingFactory, room: Room, n: int) -> None:
    for i in range(n):
        await repo.add(make_booking(room_id=room.id, start=NOW + timedelta(hours=i + 1)))


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


@pytest.mark.parametrize("sample", cases("pagination.json"))
async def test_list_room_bookings_pagination(
    async_client: httpx.AsyncClient,
    bookings_repo: InMemoryBookingsRepository,
    make_booking: BookingFactory,
    seeded_room: Room,
    sample: dict[str, Any],
) -> None:
    await _seed(bookings_repo, make_booking, seeded_room, sample["total"])
    params = {"limit": sample["limit"], "offset": sample["offset"]}
    body = (await async_client.get(f"/rooms/{seeded_room.id}/bookings", params=params)).json()
    assert body["total"] == sample["total"]
    assert body["limit"] == sample["limit"]
    assert body["offset"] == sample["offset"]
    assert len(body["bookings"]) == sample["expected_len"]


@pytest.mark.parametrize("sample", cases("time_filter.json", key="cases"))
async def test_list_room_bookings_time_filter(
    async_client: httpx.AsyncClient,
    bookings_repo: InMemoryBookingsRepository,
    make_booking: BookingFactory,
    seeded_room: Room,
    sample: dict[str, Any],
) -> None:
    for hours in TIME_FILTER["booking_start_hours"]:
        await bookings_repo.add(
            make_booking(
                room_id=seeded_room.id,
                start=NOW + timedelta(hours=hours),
                duration=timedelta(hours=TIME_FILTER["booking_duration_hours"]),
            )
        )
    params: dict[str, str] = {}
    if sample["from_hours"] is not None:
        params["from"] = (NOW + timedelta(hours=sample["from_hours"])).isoformat()
    if sample["to_hours"] is not None:
        params["to"] = (NOW + timedelta(hours=sample["to_hours"])).isoformat()

    response = await async_client.get(f"/rooms/{seeded_room.id}/bookings", params=params)
    assert response.json()["total"] == sample["expected_total"]


@pytest.mark.parametrize("sample", cases("invalid_list_query_params.json"))
async def test_list_room_bookings_invalid_query_is_422(
    async_client: httpx.AsyncClient, seeded_room: Room, sample: dict[str, Any]
) -> None:
    response = await async_client.get(f"/rooms/{seeded_room.id}/bookings", params=sample["params"])
    assert response.status_code == 422
