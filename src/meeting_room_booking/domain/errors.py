from datetime import datetime
from uuid import UUID

from meeting_room_booking.domain.booking import MAXIMUM_BOOKING_DURATION, MINIMUM_BOOKING_DURATION


class DomainError(Exception):
    """Base class for domain-specific errors."""


class InvalidRoomError(DomainError):
    def __init__(self, room_id: UUID, capacity: int) -> None:
        super().__init__(f"Invalid room cpacity with ID {room_id} and capacity {capacity}")


class InvalidBookingTimezoneError(DomainError):
    def __init__(self) -> None:
        super().__init__(f"Invalid booking timezone: start and end times must have timezone information")


class InvalidBookingStartTimeError(DomainError):
    def __init__(self, start_time: datetime) -> None:
        super().__init__(f"Invalid booking start time: {start_time} is in the past")


class InvalidBookingTimesError(DomainError):
    def __init__(self, start_time: datetime, end_time: datetime) -> None:
        super().__init__(f"Invalid booking times: start time {start_time} is not before end time {end_time}")


class InvalidBookingDurationError(DomainError):
    def __init__(self, start_time: datetime, end_time: datetime) -> None:
        super().__init__(f"Invalid booking duration: booking duration from {start_time} to {end_time} is not within the allowed range ({MINIMUM_BOOKING_DURATION} to {MAXIMUM_BOOKING_DURATION})")


class InvalidOrganizerEmailError(DomainError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Invalid organizer email: {email}")