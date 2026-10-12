from fastapi import FastAPI
from meeting_room_booking.api.routers import bookings, rooms

def create_app() -> FastAPI:
    app = FastAPI(title="Meeting Room Booking")

    app.include_router(rooms.router)
    app.include_router(bookings.router)
    
    return app