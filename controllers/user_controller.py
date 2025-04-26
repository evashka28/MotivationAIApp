from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dao.user_dao import UserDAO
from models.user import User
from core.db import get_db

router = APIRouter()

@router.post("/", response_model=dict)
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user_dao = UserDAO(db)
    existing_user = user_dao.get_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(username=username, email=email, password=password)
    user_dao.add(new_user)
    return {"id": new_user.id, "username": new_user.username}

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_dao = UserDAO(db)
    user = user_dao.get_by_id(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email}

@router.post("/login", response_model=dict)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user_dao = UserDAO(db)
    user = user_dao.get_by_email(email)
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user.id, "username": user.username, "email": user.email} 