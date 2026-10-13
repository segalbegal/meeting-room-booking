from typing import override

from meeting_room_booking.application.ports import RoomsSource
from meeting_room_booking.application.room_seeding import seed_rooms
from meeting_room_booking.domain.room import Room
from meeting_room_booking.infrastructure.in_memory import InMemoryRoomsRepository
from meeting_room_booking.infrastructure.json_rooms_source import JsonFileRoomsSource
from meeting_room_booking.main import DEFAULT_ROOMS_FILE


class StaticSource(RoomsSource):
    def __init__(self, rooms: list[Room]) -> None:
        self._rooms = rooms

    @override
    async def load(self) -> list[Room]:
        return self._rooms


async def test_seed_rooms_populates_repository(room: Room) -> None:
    repo = InMemoryRoomsRepository()
    await seed_rooms(StaticSource([room]), repo)
    assert await repo.get_all() == [room]


async def test_seed_rooms_is_idempotent(room: Room) -> None:
    repo = InMemoryRoomsRepository()
    source = StaticSource([room])
    await seed_rooms(source, repo)
    await seed_rooms(source, repo)
    assert len(await repo.get_all()) == 1


async def test_seed_from_real_json_file_end_to_end() -> None:
    repo = InMemoryRoomsRepository()
    await seed_rooms(JsonFileRoomsSource(DEFAULT_ROOMS_FILE), repo)
    names = {r.name for r in await repo.get_all()}
    assert names == {"Everest", "Kilimanjaro", "Denali", "Elbrus", "Fuji"}
