from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True, slots=True, kw_only=True)
class Room(BaseModel):
    id: UUID
    name: str
    capacity: int

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("Capacity must be a positive integer")