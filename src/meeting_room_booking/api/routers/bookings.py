from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("")
def get_bookings() -> list[dict]:
    return [{"message": "List of bookings"}]