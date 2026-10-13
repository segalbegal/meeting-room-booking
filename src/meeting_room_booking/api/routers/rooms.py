from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import AwareDatetime

from meeting_room_booking.api import mappers
from meeting_room_booking.api.dependencies import BookingsRepositoryDep, RoomsRepositoryDep
from meeting_room_booking.api.models import schemas
from meeting_room_booking.application import booking_service


ROOM_BOOKINGS_MIN: int = 1
ROOM_BOOKINGS_MAX: int = 100

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("")
async def list_rooms(rooms: RoomsRepositoryDep) -> list[schemas.Room]:
    return [mappers.to_room(room) for room in await rooms.get_all()]


@router.get("/{room_id}/bookings")
async def list_room_bookings(
    room_id: UUID,
    rooms: RoomsRepositoryDep,
    bookings: BookingsRepositoryDep,
    from_: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    to: AwareDatetime | None = None,
    limit: Annotated[int, Query(ge=ROOM_BOOKINGS_MIN, le=ROOM_BOOKINGS_MAX)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> schemas.BookingsPage:
    if await rooms.get_by_id(room_id) is None:
        raise HTTPException(status_code=404, detail="Room not found")
    page = await booking_service.list_room_bookings(bookings, room_id, from_, to, limit, offset)
    return schemas.BookingsPage(
        bookings=[mappers.to_booking(booking) for booking in page.bookings],
        total=page.total,
        limit=limit,
        offset=offset,
    )
