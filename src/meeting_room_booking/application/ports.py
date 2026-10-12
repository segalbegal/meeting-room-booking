from typing import Protocol


class RoomsRepository:
    async def get_all_rooms(self) -> list[dict]:
        raise NotImplementedError


class BookingsRepository(Protocol):
    pass