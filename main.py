from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from core.conf import GIGACHAT_TOKEN
from core.db import Session, engine
from dao.character_dao import CharacterDAO
from models.user import User
from models.habit import Habit
from models.event import Event
from dao.user_dao import UserDAO
from dao.habit_dao import HabitDAO
from dao.event_dao import EventDAO
from services.habit_forecast import HabitForecastService

#команда для запуска сервера uvicorn main:app --reload

app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# DAO
@app.post("/users/", response_model=dict)
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user_dao = UserDAO(db)
    existing_user = user_dao.get_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(username=username, email=email, password=password)
    user_dao.add(new_user)
    return {"id": new_user.id, "username": new_user.username}


@app.get("/users/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_dao = UserDAO(db)
    user = user_dao.get_by_id(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email}

@app.post("/login", response_model=dict)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user_dao = UserDAO(db)
    user = user_dao.get_by_email(email)
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user.id, "username": user.username, "email": user.email}


@app.post("/habits/", response_model=dict)
def create_habit(name: str, description: str, user_id: int, repeat: str, difficulty: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    new_habit = Habit(name=name, description=description, user_id=user_id, repeat=repeat, difficulty=difficulty)
    habit_dao.add(new_habit)
    return {"id": new_habit.id, "name": new_habit.name}


@app.get("/habits/{habit_id}", response_model=dict)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    habit = habit_dao.get_by_id(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"id": habit.id, "name": habit.name, "is_recurring": habit.is_recurring}

@app.get("/users/{user_id}/habits", response_model=list)
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


@app.post("/events/", response_model=dict)
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

    experience_gain = 5 * habit.difficulty  # 1 -> 5, 2 -> 10, 3 -> 15

    if character:
        character_dao.update_experience(character.id, experience_gain)

    return {"success": True, "id": new_event.id, "execution_time": new_event.execution_time}


@app.get("/events/{habit_id}", response_model=list)
def get_events_by_habit(habit_id: int, db: Session = Depends(get_db)):
    event_dao = EventDAO(db)
    events = event_dao.get_by_habit_id(habit_id)
    return [{"id": event.id, "habit_id": event.habit_id, "execution_time": event.execution_time} for event in events]

@app.post("/characters/", response_model=dict)
def create_character(user_id: int, name: str, db: Session = Depends(get_db)):
    character_dao = CharacterDAO(db)
    character = character_dao.create_character(user_id=user_id, name=name)
    return {
        "id": character.id,
        "name": character.name,
        "level": character.level,
        "experience": character.experience,
        "max_experience": character.max_experience,
        "current_health": character.current_health,
        "max_health": character.max_health,
        "avatar": character.avatar,
    }

@app.get("/characters/{user_id}", response_model=dict)
def get_character(user_id: int, db: Session = Depends(get_db)):
    character_dao = CharacterDAO(db)
    character = character_dao.get_by_user_id(user_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return {
        "id": character.id,
        "name": character.name,
        "level": character.level,
        "experience": character.experience,
        "max_experience": character.max_experience,
        "current_health": character.current_health,
        "max_health": character.max_health,
        "avatar": character.avatar,
    }


@app.get("/habits/{habit_id}/progress", response_model=dict)
def get_habit_progress(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    event_dao = EventDAO(db)

    habit = habit_dao.get_by_id(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    current_count = event_dao.get_current_period_event_count(habit)

    # Определяем максимум
    repeat = habit.repeat.lower()
    if repeat.startswith("1 раз"):
        max_count = 1
    elif repeat.startswith("2 раза"):
        max_count = 2
    elif repeat.startswith("3 раза"):
        max_count = 3
    else:
        max_count = 1  # дефолт на случай странного значения

    return {
        "habit_id": habit.id,
        "current": current_count,
        "max": max_count
    }


@app.get("/habits/{habit_id}/forecast", response_model=dict)
def forecast_habit(habit_id: int, db: Session = Depends(get_db)):
    forecast_service = HabitForecastService(
        db,
        client_id="",
        client_secret=""
    )

    declining = forecast_service.is_habit_declining(habit_id)
    print(GIGACHAT_TOKEN)
    alternatives = []
    if declining:
        alternatives = forecast_service.generate_alternatives(habit_id)
        # Если вдруг меньше 3 — добиваем пустыми строками, чтобы на клиенте был стабильный формат
        while len(alternatives) < 3:
            alternatives.append("")

    return {
        "habit_id": habit_id,
        "declining": bool(declining),
        "alternative_1": alternatives[0] if alternatives else "",
        "alternative_2": alternatives[1] if alternatives else "",
        "alternative_3": alternatives[2] if alternatives else ""
    }

@app.delete("/habits/{habit_id}", response_model=dict)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    success = habit_dao.delete_with_events(habit_id)

    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")

    return {"success": True, "message": f"Habit {habit_id} and its events have been deleted"}

