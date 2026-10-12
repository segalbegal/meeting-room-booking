from typing import Iterator

from fastapi import APIRouter

from meeting_room_booking.domain.booking import Booking

router = APIRouter(prefix="/bookings", tags=["bookings"])