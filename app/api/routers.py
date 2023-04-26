from fastapi import APIRouter

from app.api.endpionts import (
    user_router,
)


main_router = APIRouter()

main_router.include_router(user_router)
