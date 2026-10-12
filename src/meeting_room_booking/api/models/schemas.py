from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class BookingStatus(str, Enum):
    active = "active"
    cancelled = "cancelled"


class Room(BaseModel):
    id: UUID
    name: str
    capacity: int


class BookingCreate(BaseModel):
    room_id: UUID
    title: str | None
    organizer_email: str
    start: datetime
    end: datetime


class Booking(BookingCreate):
    id: UUID
    status: BookingStatus = BookingStatus.active
    created_at: datetime


class BookingsPage(BaseModel):
    bookings: list[Booking]
    total: int
    limit: int
    offset: int
