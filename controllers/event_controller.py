from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dao.event_dao import EventDAO
from dao.habit_dao import HabitDAO
from dao.character_dao import CharacterDAO
from models.event import Event
from models.habit import Habit
from core.db import get_db

router = APIRouter()

@router.post("/", response_model=dict)
def create_event(habit_id: int, db: Session = Depends(get_db)):
    event_dao = EventDAO(db)
    habit_dao = HabitDAO(db)
    habit = habit_dao.get_by_id(Habit, habit_id)

    if not event_dao.can_register_event(habit):
        return {"success": False, "message": "Нельзя выполнить привычку чаще, чем задано"}

    new_event = Event(habit_id=habit_id)
    event_dao.add_event(new_event)

    character_dao = CharacterDAO(db)
    character = character_dao.get_by_user_id(habit.user_id)

    experience_gain = 5 * habit.difficulty

    if character:
        character_dao.update_experience(character.id, experience_gain)

    return {"success": True, "id": new_event.id, "execution_time": new_event.execution_time}

@router.get("/{habit_id}", response_model=list)
def get_events_by_habit(habit_id: int, db: Session = Depends(get_db)):
    event_dao = EventDAO(db)
    events = event_dao.get_by_habit_id(habit_id)
    return [{"id": event.id, "habit_id": event.habit_id, "execution_time": event.execution_time} for event in events] 