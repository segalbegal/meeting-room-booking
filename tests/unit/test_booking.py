from datetime import UTC, datetime, timedelta, timezone

import pytest

from meeting_room_booking.domain.booking import (
    MAXIMUM_BOOKING_DURATION,
    MINIMUM_BOOKING_DURATION,
    BookingStatus,
    has_timezone,
)
from meeting_room_booking.domain.errors import (
    InvalidBookingDurationError,
    InvalidBookingStartTimeError,
    InvalidBookingTimesError,
    InvalidBookingTimezoneError,
    InvalidOrganizerEmailError,
)
from tests.conftest import NOW, BookingFactory, FakeClock


def test_has_timezone() -> None:
    assert has_timezone(datetime(2030, 1, 1, tzinfo=UTC))
    assert has_timezone(datetime(2030, 1, 1, tzinfo=timezone(timedelta(hours=2))))
    assert not has_timezone(datetime(2030, 1, 1))


def test_valid_booking_is_created(make_booking: BookingFactory) -> None:
    booking = make_booking()
    assert booking.status is BookingStatus.active
    assert booking.end - booking.start == timedelta(hours=1)


def test_title_is_optional(make_booking: BookingFactory) -> None:
    assert make_booking(title=None).title is None


@pytest.mark.parametrize("duration", [MINIMUM_BOOKING_DURATION, MAXIMUM_BOOKING_DURATION])
def test_duration_boundaries_are_inclusive(make_booking: BookingFactory, duration: timedelta) -> None:
    booking = make_booking(duration=duration)
    assert booking.end - booking.start == duration


@pytest.mark.parametrize(
    "duration",
    [MINIMUM_BOOKING_DURATION - timedelta(seconds=1), MAXIMUM_BOOKING_DURATION + timedelta(seconds=1)],
)
def test_duration_outside_range_is_rejected(make_booking: BookingFactory, duration: timedelta) -> None:
    with pytest.raises(InvalidBookingDurationError):
        make_booking(duration=duration)


@pytest.mark.parametrize("duration", [timedelta(0), timedelta(hours=-1)])
def test_end_not_after_start_is_rejected(make_booking: BookingFactory, duration: timedelta) -> None:
    with pytest.raises(InvalidBookingTimesError):
        make_booking(duration=duration)


def test_naive_datetimes_are_rejected(make_booking: BookingFactory) -> None:
    with pytest.raises(InvalidBookingTimezoneError):
        make_booking(start=datetime(2030, 1, 1, 10))


def test_organizer_email_without_at_sign_is_rejected(make_booking: BookingFactory) -> None:
    with pytest.raises(InvalidOrganizerEmailError, match="not-an-email"):
        make_booking(organizer_email="not-an-email")


def test_start_in_past_is_rejected(make_booking: BookingFactory, clock: FakeClock) -> None:
    booking = make_booking(start=NOW - timedelta(minutes=1))
    with pytest.raises(InvalidBookingStartTimeError):
        booking.validate_start_not_in_past(clock)


@pytest.mark.parametrize("offset", [timedelta(0), timedelta(hours=1)])
def test_start_now_or_future_is_accepted(make_booking: BookingFactory, clock: FakeClock, offset: timedelta) -> None:
    make_booking(start=NOW + offset).validate_start_not_in_past(clock)


def test_booking_is_immutable(make_booking: BookingFactory) -> None:
    booking = make_booking()
    with pytest.raises(AttributeError):
        booking.title = "changed"  # type: ignore[misc]
