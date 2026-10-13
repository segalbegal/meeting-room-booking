from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import pytest

from meeting_room_booking.domain.booking import BookingStatus, has_timezone
from meeting_room_booking.domain.errors import InvalidBookingStartTimeError
from tests.conftest import NOW, BookingFactory, FakeClock
from tests.helpers import cases, domain_error


def test_has_timezone() -> None:
    assert has_timezone(datetime(2030, 1, 1, tzinfo=UTC))
    assert has_timezone(datetime(2030, 1, 1, tzinfo=timezone(timedelta(hours=2))))
    assert not has_timezone(datetime(2030, 1, 1))


def test_valid_booking_defaults(make_booking: BookingFactory) -> None:
    booking = make_booking()
    assert booking.status is BookingStatus.active
    assert booking.end - booking.start == timedelta(hours=1)


def test_title_is_optional(make_booking: BookingFactory) -> None:
    assert make_booking(title=None).title is None


@pytest.mark.parametrize("sample", cases("booking_creation.json"))
def test_booking_creation(make_booking: BookingFactory, sample: dict[str, Any]) -> None:
    kwargs: dict[str, Any] = {"duration": timedelta(seconds=sample["duration_seconds"])}
    if sample.get("naive_start"):
        kwargs["start"] = datetime(2030, 1, 1, 10)
    if "organizer_email" in sample:
        kwargs["organizer_email"] = sample["organizer_email"]

    expected_error = domain_error(sample["error"])
    if expected_error is None:
        booking = make_booking(**kwargs)
        assert booking.end - booking.start == kwargs["duration"]
    else:
        with pytest.raises(expected_error):
            make_booking(**kwargs)


@pytest.mark.parametrize("sample", cases("booking_start_times.json"))
def test_start_not_in_past_validation(
    make_booking: BookingFactory, clock: FakeClock, sample: dict[str, Any]
) -> None:
    booking = make_booking(start=NOW + timedelta(seconds=sample["offset_seconds"]))
    if sample["accepted"]:
        booking.validate_start_not_in_past(clock)
    else:
        with pytest.raises(InvalidBookingStartTimeError):
            booking.validate_start_not_in_past(clock)


def test_booking_is_immutable(make_booking: BookingFactory) -> None:
    booking = make_booking()
    with pytest.raises(AttributeError):
        booking.title = "changed"  # type: ignore[misc]
