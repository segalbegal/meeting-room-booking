from typing import Annotated, cast

from fastapi import Depends, Request

from meeting_room_booking.application.ports import BookingsRepository, RoomsRepository
from meeting_room_booking.domain.clock import Clock


def get_rooms_repository(request: Request) -> RoomsRepository:
    return cast(RoomsRepository, request.app.state.rooms_repository)


def get_bookings_repository(request: Request) -> BookingsRepository:
    return cast(BookingsRepository, request.app.state.bookings_repository)


def get_clock(request: Request) -> Clock:
    return cast(Clock, request.app.state.clock)


RoomsRepositoryDep = Annotated[RoomsRepository, Depends(get_rooms_repository)]
BookingsRepositoryDep = Annotated[BookingsRepository, Depends(get_bookings_repository)]
ClockDep = Annotated[Clock, Depends(get_clock)]
