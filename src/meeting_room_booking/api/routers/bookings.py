from uuid import UUID

from fastapi import APIRouter, HTTPException

from meeting_room_booking.api import mappers
from meeting_room_booking.api.dependencies import BookingsRepositoryDep
from meeting_room_booking.api.models import schemas

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/{booking_id}")
async def get_booking(booking_id: UUID, bookings: BookingsRepositoryDep) -> schemas.Booking:
    booking = await bookings.get_by_id(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return mappers.to_booking(booking)
