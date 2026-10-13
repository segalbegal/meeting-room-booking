from uuid import uuid4

from fastapi.testclient import TestClient

from meeting_room_booking.domain.room import Room
from meeting_room_booking.main import create_app


def test_list_rooms_returns_seeded_rooms(client: TestClient, room: Room) -> None:
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json() == [{"id": str(room.id), "name": room.name, "capacity": room.capacity}]


def test_default_app_seeds_rooms_from_bundled_json() -> None:
    with TestClient(create_app()) as c:
        assert len(c.get("/rooms").json()) == 5


def test_list_bookings_of_unknown_room_is_404(client: TestClient) -> None:
    response = client.get(f"/rooms/{uuid4()}/bookings")
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found"}


def test_list_bookings_with_invalid_room_id_is_422(client: TestClient) -> None:
    assert client.get("/rooms/not-a-uuid/bookings").status_code == 422


def test_list_bookings_empty_room(client: TestClient, room: Room) -> None:
    response = client.get(f"/rooms/{room.id}/bookings")
    assert response.status_code == 200
    assert response.json() == {"bookings": [], "total": 0, "limit": 50, "offset": 0}
