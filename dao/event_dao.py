from sqlalchemy import func
from sqlalchemy.orm import Session
from models.event import Event
from dao.base_dao import BaseDAO


class EventDAO(BaseDAO):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_habit_id(self, habit_id: int):
        """Получить все события для привычки."""
        return self.session.query(Event).filter_by(habit_id=habit_id).all()

    def get_today_events(self, habit_id: int):
        """Получить события для привычки за текущий день."""
        from datetime import date
        today = date.today()
        return self.session.query(Event).filter(
            Event.habit_id == habit_id,
            func.date(Event.execution_time) == today
        ).all()
