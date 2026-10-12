from typing import Annotated, cast
from fastapi import Depends, Request


def get_rooms_repository() -> RoomsRepository:
    return InMemoryRoomRepository()


RoomsRepositoryDep = Annotated[RoomsRepository, Depends(get_rooms_repository)]