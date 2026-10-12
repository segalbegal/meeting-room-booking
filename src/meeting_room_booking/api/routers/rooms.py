from fastapi import APIRouter

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("")
def get_rooms() -> list[dict]:
    return [{"message": "List of rooms"}]