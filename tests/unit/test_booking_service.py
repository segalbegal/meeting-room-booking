from datetime import timedelta
from uuid import UUID, uuid4

from meeting_room_booking.application.booking_service import list_room_bookings
from meeting_room_booking.infrastructure.in_memory import InMemoryBookingsRepository
from tests.conftest import NOW, BookingFactory


async def _repo_with_bookings(
    make_booking: BookingFactory, count: int
) -> tuple[InMemoryBookingsRepository, UUID]:
    repo = InMemoryBookingsRepository()
    room_id = uuid4()
    # inserted in reverse so sorting is actually exercised
    for i in reversed(range(count)):
        await repo.add(make_booking(room_id=room_id, start=NOW + timedelta(hours=i + 1)))
    return repo, room_id


async def test_bookings_are_sorted_by_start(make_booking: BookingFactory) -> None:
    repo, room_id = await _repo_with_bookings(make_booking, 3)
    page = await list_room_bookings(repo, room_id, None, None, limit=10, offset=0)
    starts = [b.start for b in page.bookings]
    assert starts == sorted(starts)
    assert page.total == 3


async def test_pagination_slices_but_total_is_full_count(make_booking: BookingFactory) -> None:
    repo, room_id = await _repo_with_bookings(make_booking, 5)
    page = await list_room_bookings(repo, room_id, None, None, limit=2, offset=2)
    assert len(page.bookings) == 2
    assert page.total == 5


async def test_offset_beyond_total_gives_empty_page(make_booking: BookingFactory) -> None:
    repo, room_id = await _repo_with_bookings(make_booking, 2)
    page = await list_room_bookings(repo, room_id, None, None, limit=10, offset=10)
    assert page.bookings == []
    assert page.total == 2


async def test_no_bookings() -> None:
    page = await list_room_bookings(InMemoryBookingsRepository(), uuid4(), None, None, 10, 0)
    assert page.bookings == []
    assert page.total == 0
