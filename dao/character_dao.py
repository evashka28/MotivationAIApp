from core.db import Session
from dao.base_dao import BaseDAO
from models.character import Character


class CharacterDAO(BaseDAO):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_user_id(self, user_id: int):
        """Получить персонажа по ID пользователя"""
        return self.session.query(Character).filter_by(user_id=user_id).first()

    def create_character(self, user_id: int, name: str):
        """Создать персонажа для пользователя"""
        new_character = Character(user_id=user_id, name=name)
        self.add(new_character)
        return new_character

    def update_experience(self, character_id: int, experience: int):
        """Обновить опыт персонажа"""
        character = self.get_by_id(Character, character_id)
        character.experience += experience
        if character.experience >= character.max_experience:
            character.level += 1
            character.experience = 0
            character.max_experience = character.level * 50
        self.session.commit()
        return character
