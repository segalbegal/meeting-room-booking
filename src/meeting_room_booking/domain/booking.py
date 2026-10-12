from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from meeting_room_booking.domain.clock import Clock
from meeting_room_booking.domain.errors import InvalidBookingDurationError, InvalidBookingStartTimeError, InvalidBookingTimesError, InvalidBookingTimezoneError, InvalidOrganizerEmailError


MINIMUM_BOOKING_DURATION = timedelta(minutes=15)
MAXIMUM_BOOKING_DURATION = timedelta(hours=4)


def has_timezone(date: datetime) -> bool:
    return date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None


class BookingStatus(Enum):
    active = "active"
    cancelled = "cancelled"


@dataclass(frozen=True, slots=True, kw_only=True)
class Booking(BaseModel):
    id: UUID
    room_id: UUID
    title: str | None
    organizer_email: str
    start: datetime
    end: datetime
    status: BookingStatus
    created_at: datetime

    def __post_init__(self) -> None:
        if not has_timezone(self.start) or not has_timezone(self.end):
            raise InvalidBookingTimezoneError()
        if self.start >= self.end:
            raise InvalidBookingTimesError(self.start, self.end)
        if self.end - self.start > MAXIMUM_BOOKING_DURATION or self.end - self.start < MINIMUM_BOOKING_DURATION:
            raise InvalidBookingDurationError(self.start, self.end)
        if self.organizer_email and "@" not in self.organizer_email:
            raise InvalidOrganizerEmailError(self.organizer_email)

    def validate_start_not_in_past(self, clock: Clock) -> None:
        if self.start < clock.now():
            raise InvalidBookingStartTimeError(self.start)
