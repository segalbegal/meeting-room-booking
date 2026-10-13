import json
from pathlib import Path
from typing import override
from uuid import UUID

from meeting_room_booking.application.ports import RoomsSource
from meeting_room_booking.domain.room import Room


class JsonFileRoomsSource(RoomsSource):
    def __init__(self, path: Path) -> None:
        self._path = path

    @override
    async def load(self) -> list[Room]:
        items = json.loads(self._path.read_text(encoding="utf-8"))
        return [
            Room(id=UUID(item["id"]), name=item["name"], capacity=item["capacity"])
            for item in items
        ]
