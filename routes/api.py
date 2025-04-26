from fastapi import APIRouter
from controllers import user_controller, habit_controller, event_controller, character_controller

router = APIRouter()

router.include_router(user_controller.router, prefix="/users", tags=["users"])
router.include_router(habit_controller.router, prefix="/habits", tags=["habits"])
router.include_router(event_controller.router, prefix="/events", tags=["events"])
router.include_router(character_controller.router, prefix="/characters", tags=["characters"]) 