from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import Session, engine
from models.base import Base
from models.user import User
from models.habit import Habit
from models.event import Event
from dao.user_dao import UserDAO
from dao.habit_dao import HabitDAO
from dao.event_dao import EventDAO

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


@app.post("/habits/", response_model=dict)
def create_habit(name: str, description: str, user_id: int, repeat: str, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    new_habit = Habit(name=name, description=description, user_id=user_id, repeat=repeat)
    habit_dao.add(new_habit)
    return {"id": new_habit.id, "name": new_habit.name}


@app.get("/habits/{habit_id}", response_model=dict)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit_dao = HabitDAO(db)
    habit = habit_dao.get_by_id(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"id": habit.id, "name": habit.name, "is_recurring": habit.is_recurring}


@app.post("/events/", response_model=dict)
def create_event(habit_id: int, db: Session = Depends(get_db)):
    event_dao = EventDAO(db)
    new_event = Event(habit_id=habit_id)
    event_dao.add(new_event)
    return {"id": new_event.id, "execution_time": new_event.execution_time}


@app.get("/events/{habit_id}", response_model=list)
def get_events_by_habit(habit_id: int, db: Session = Depends(get_db)):
    event_dao = EventDAO(db)
    events = event_dao.get_by_habit_id(habit_id)
    return [{"id": event.id, "execution_time": event.execution_time} for event in events]
