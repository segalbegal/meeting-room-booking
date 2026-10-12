from datetime import datetime
from enum import Enum
from typing import Iterator

from pydantic import BaseModel


class BookingStatus(str, Enum):
    active = "active"
    cancelled = "cancelled"


class RoomsPage(BaseModel):
    rooms: Iterator[Room]
    total: int


class Room(BaseModel):
    id: int
    name: str
    capacity: int


class BookingCreate(BaseModel):
    room_id: int
    title: str
    organizer_email: str
    start: datetime
    end: datetime


class Booking(BookingCreate):
    id: int
    status: BookingStatus = BookingStatus.active
    created_at: datetime
