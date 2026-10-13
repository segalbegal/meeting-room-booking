from datetime import UTC, datetime
from typing import override

from meeting_room_booking.domain.clock import Clock


class SystemClock(Clock):
    @override
    def now(self) -> datetime:
        return datetime.now(UTC)
