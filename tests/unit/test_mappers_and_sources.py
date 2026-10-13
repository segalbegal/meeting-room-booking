import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from meeting_room_booking.api import mappers
from meeting_room_booking.api.models import schemas
from meeting_room_booking.domain.booking import BookingStatus
from meeting_room_booking.domain.room import Room
from meeting_room_booking.infrastructure.json_rooms_source import JsonFileRoomsSource
from meeting_room_booking.infrastructure.system_clock import SystemClock
from meeting_room_booking.main import DEFAULT_ROOMS_FILE
from tests.conftest import BookingFactory


def test_to_room(room: Room) -> None:
    dto = mappers.to_room(room)
    assert (dto.id, dto.name, dto.capacity) == (room.id, room.name, room.capacity)


def test_to_booking_maps_all_fields_and_status(make_booking: BookingFactory) -> None:
    booking = make_booking(status=BookingStatus.cancelled)
    dto = mappers.to_booking(booking)
    assert dto.id == booking.id
    assert dto.room_id == booking.room_id
    assert dto.organizer_email == booking.organizer_email
    assert dto.start == booking.start
    assert dto.end == booking.end
    assert dto.created_at == booking.created_at
    assert dto.status is schemas.BookingStatus.cancelled


async def test_json_source_loads_rooms(tmp_path: Path) -> None:
    room_id = uuid4()
    path = tmp_path / "rooms.json"
    path.write_text(json.dumps([{"id": str(room_id), "name": "A", "capacity": 4}]), encoding="utf-8")
    rooms = await JsonFileRoomsSource(path).load()
    assert rooms == [Room(id=room_id, name="A", capacity=4)]


async def test_json_source_rejects_invalid_capacity(tmp_path: Path) -> None:
    path = tmp_path / "rooms.json"
    path.write_text(json.dumps([{"id": str(uuid4()), "name": "A", "capacity": 0}]), encoding="utf-8")
    with pytest.raises(ValueError):
        await JsonFileRoomsSource(path).load()


async def test_json_source_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        await JsonFileRoomsSource(tmp_path / "nope.json").load()


async def test_bundled_rooms_file_is_valid() -> None:
    rooms = await JsonFileRoomsSource(DEFAULT_ROOMS_FILE).load()
    assert len(rooms) == 5
    assert len({r.id for r in rooms}) == 5
    assert all(isinstance(r.id, UUID) for r in rooms)


def test_system_clock_returns_aware_utc_time() -> None:
    offset = SystemClock().now().utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 0
