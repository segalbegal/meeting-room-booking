from datetime import timedelta
from uuid import uuid4

from meeting_room_booking.domain.booking import BookingStatus
from meeting_room_booking.domain.room import Room
from meeting_room_booking.infrastructure.in_memory import (
    InMemoryBookingsRepository,
    InMemoryRoomsRepository,
)
from tests.conftest import NOW, BookingFactory


async def test_rooms_add_get_and_list(room: Room) -> None:
    repo = InMemoryRoomsRepository()
    assert await repo.get_all() == []
    await repo.add(room)
    assert await repo.get_by_id(room.id) == room
    assert await repo.get_all() == [room]


async def test_rooms_get_unknown_returns_none() -> None:
    assert await InMemoryRoomsRepository().get_by_id(uuid4()) is None


async def test_rooms_add_same_id_overwrites(room: Room) -> None:
    repo = InMemoryRoomsRepository()
    await repo.add(room)
    await repo.add(Room(id=room.id, name="Renamed", capacity=3))
    assert [r.name for r in await repo.get_all()] == ["Renamed"]


async def test_bookings_add_and_get(make_booking: BookingFactory) -> None:
    repo = InMemoryBookingsRepository()
    booking = make_booking()
    await repo.add(booking)
    assert await repo.get_by_id(booking.id) == booking
    assert await repo.get_by_id(uuid4()) is None


async def test_active_for_room_filters_by_room_and_status(make_booking: BookingFactory) -> None:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    mine = make_booking(room_id=room_id)
    await repo.add(mine)
    await repo.add(make_booking(room_id=room_id, status=BookingStatus.cancelled))
    await repo.add(make_booking(room_id=uuid4()))
    assert await repo.get_active_for_room(room_id, None, None) == [mine]


async def test_active_for_room_overlap_is_half_open(make_booking: BookingFactory) -> None:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    booking = make_booking(room_id=room_id, start=NOW + timedelta(hours=2), duration=timedelta(hours=1))
    await repo.add(booking)

    # window ending exactly when booking starts / starting exactly when it ends: no overlap
    assert await repo.get_active_for_room(room_id, None, booking.start) == []
    assert await repo.get_active_for_room(room_id, booking.end, None) == []
    # one-second overlap on either side
    assert await repo.get_active_for_room(room_id, None, booking.start + timedelta(seconds=1)) == [booking]
    assert await repo.get_active_for_room(room_id, booking.end - timedelta(seconds=1), None) == [booking]
