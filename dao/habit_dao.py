from sqlalchemy.orm import Session

from models import Event
from models.habit import Habit
from dao.base_dao import BaseDAO

class HabitDAO(BaseDAO):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_user_id(self, user_id: int):
        """Получить все привычки пользователя."""
        return self.session.query(Habit).filter_by(user_id=user_id).all()

    def delete_with_events(self, habit_id: int):
        habit = self.get_by_id(Habit, habit_id)
        if not habit:
            return False

        # Удаляем события привычки
        self.session.query(Event).filter_by(habit_id=habit_id).delete()
        # Удаляем саму привычку
        self.session.delete(habit)
        self.session.commit()
        return True


