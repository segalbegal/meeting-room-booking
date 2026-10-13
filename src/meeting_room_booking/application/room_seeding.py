from meeting_room_booking.application.ports import RoomsRepository, RoomsSource


async def seed_rooms(source: RoomsSource, repository: RoomsRepository) -> None:
    for room in await source.load():
        await repository.add(room)
