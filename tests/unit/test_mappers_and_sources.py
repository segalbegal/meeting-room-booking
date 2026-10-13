import json
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from meeting_room_booking.api import mappers
from meeting_room_booking.api.models import schemas
from meeting_room_booking.domain.booking import BookingStatus
from meeting_room_booking.domain.room import Room
from meeting_room_booking.infrastructure.json_rooms_source import JsonFileRoomsSource
from meeting_room_booking.infrastructure.system_clock import SystemClock
from meeting_room_booking.main import DEFAULT_ROOMS_FILE
from tests.conftest import BookingFactory
from tests.helpers import cases


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


def _write_source(tmp_path: Path, sample: dict[str, Any]) -> JsonFileRoomsSource:
    path = tmp_path / "rooms.json"
    path.write_text(json.dumps([sample]), encoding="utf-8")
    return JsonFileRoomsSource(path)


@pytest.mark.parametrize("sample", cases("rooms_valid.json"))
async def test_json_source_loads_valid_room(tmp_path: Path, sample: dict[str, Any]) -> None:
    rooms = await _write_source(tmp_path, sample).load()
    assert rooms == [Room(id=UUID(sample["id"]), name=sample["name"], capacity=sample["capacity"])]


@pytest.mark.parametrize("sample", cases("rooms_invalid.json"))
async def test_json_source_rejects_invalid_room(tmp_path: Path, sample: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        await _write_source(tmp_path, sample).load()


async def test_json_source_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        await JsonFileRoomsSource(tmp_path / "nope.json").load()


async def test_bundled_rooms_file_is_valid() -> None:
    rooms = await JsonFileRoomsSource(DEFAULT_ROOMS_FILE).load()
    assert len(rooms) == 5
    assert len({r.id for r in rooms}) == 5


def test_system_clock_returns_aware_utc_time() -> None:
    offset = SystemClock().now().utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 0
