from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dao.habit_dao import HabitDAO
from models.habit import Habit
from core.db import get_db
from services.habit_forecast import HabitForecastService

router = APIRouter()

@router.post("/", response_model=dict)
def create_habit(name: str, description: str, user_id: int, repeat: str, difficulty: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    new_habit = Habit(name=name, description=description, user_id=user_id, repeat=repeat, difficulty=difficulty)
    habit_dao.add(new_habit)
    return {"id": new_habit.id, "name": new_habit.name}

@router.get("/{habit_id}", response_model=dict)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    habit = habit_dao.get_by_id(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"id": habit.id, "name": habit.name, "is_recurring": habit.is_recurring}

@router.get("/users/{user_id}", response_model=list)
def get_habits_by_user_id(user_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    habits = habit_dao.get_by_user_id(user_id)
    if not habits:
        raise HTTPException(status_code=404, detail="No habits found for this user")
    return [
        {
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
            "repeat": habit.repeat,
            "created_at": habit.create_at,
            "difficulty": habit.difficulty
        }
        for habit in habits
    ]

@router.get("/{habit_id}/progress", response_model=dict)
def get_habit_progress(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    event_dao = EventDAO(db)

    habit = habit_dao.get_by_id(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    current_count = event_dao.get_current_period_event_count(habit)

    repeat = habit.repeat.lower()
    if repeat.startswith("1 раз"):
        max_count = 1
    elif repeat.startswith("2 раза"):
        max_count = 2
    elif repeat.startswith("3 раза"):
        max_count = 3
    else:
        max_count = 1

    return {
        "habit_id": habit.id,
        "current": current_count,
        "max": max_count
    }

@router.get("/{habit_id}/forecast", response_model=dict)
def forecast_habit(habit_id: int, db: Session = Depends(get_db)):
    forecast_service = HabitForecastService(db)
    declining = forecast_service.is_habit_declining(habit_id)
    alternatives = []
    if declining:
        alternatives = forecast_service.generate_alternatives(habit_id)
        while len(alternatives) < 3:
            alternatives.append("")

    return {
        "habit_id": habit_id,
        "declining": bool(declining),
        "alternative_1": alternatives[0] if alternatives else "",
        "alternative_2": alternatives[1] if alternatives else "",
        "alternative_3": alternatives[2] if alternatives else ""
    }

@router.delete("/{habit_id}", response_model=dict)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    success = habit_dao.delete_with_events(habit_id)

    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")

    return {"success": True, "message": f"Habit {habit_id} and its events have been deleted"} 