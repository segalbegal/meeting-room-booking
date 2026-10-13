from meeting_room_booking.api.models import schemas
from meeting_room_booking.domain.booking import Booking
from meeting_room_booking.domain.room import Room


def to_room(room: Room) -> schemas.Room:
    return schemas.Room(id=room.id, name=room.name, capacity=room.capacity)


def to_booking(booking: Booking) -> schemas.Booking:
    return schemas.Booking(
        id=booking.id,
        room_id=booking.room_id,
        title=booking.title,
        organizer_email=booking.organizer_email,
        start=booking.start,
        end=booking.end,
        status=schemas.BookingStatus(booking.status.value),
        created_at=booking.created_at,
    )
