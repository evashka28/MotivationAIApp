from sqlalchemy.orm import Session
from models.habit import Habit
from dao.base_dao import BaseDAO

class HabitDAO(BaseDAO):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_user_id(self, user_id: int):
        """Получить все привычки пользователя."""
        return self.session.query(Habit).filter_by(user_id=user_id).all()


