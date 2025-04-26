from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dao.character_dao import CharacterDAO
from core.db import get_db

router = APIRouter()

@router.post("/", response_model=dict)
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

@router.get("/{user_id}", response_model=dict)
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