from collections.abc import Iterable

from fastapi import APIRouter

from meeting_room_booking.domain.room import Room

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("")
async def list_rooms() -> RoomsPage:
    pass
    # return [{"message": "List of rooms"}]