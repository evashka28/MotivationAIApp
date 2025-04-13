from datetime import timedelta, date

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Habit
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

    def get_last_event_date(self, habit_id: int):
        return self.session.query(Event).filter_by(habit_id=habit_id).order_by(Event.execution_time.desc()).first()

    def can_register_event(self, habit: Habit):
        last_event = self.get_last_event_date(habit.id)
        if not last_event:
            return True

        last_date = last_event.execution_time.date()
        today = date.today()

        repeat = habit.repeat.lower()

        if repeat == "1 раз в день":
            return last_date < today
        elif repeat == "2 раза в день":
            events_today = self.session.query(Event).filter(
                Event.habit_id == habit.id,
                func.date(Event.execution_time) == today
            ).count()
            return events_today < 2
        elif repeat == "3 раза в неделю":
            start_of_week = today - timedelta(days=today.weekday())
            count = self.session.query(Event).filter(
                Event.habit_id == habit.id,
                Event.execution_time >= start_of_week
            ).count()
            return count < 3
        elif repeat == "2 раза в неделю":
            start_of_week = today - timedelta(days=today.weekday())
            count = self.session.query(Event).filter(
                Event.habit_id == habit.id,
                Event.execution_time >= start_of_week
            ).count()
            return count < 2
        elif repeat == "1 раз в неделю":
            start_of_week = today - timedelta(days=today.weekday())
            count = self.session.query(Event).filter(
                Event.habit_id == habit.id,
                Event.execution_time >= start_of_week
            ).count()
            return count < 1
        elif repeat == "1 раз в месяц":
            start_of_month = today.replace(day=1)
            count = self.session.query(Event).filter(
                Event.habit_id == habit.id,
                Event.execution_time >= start_of_month
            ).count()
            return count < 1

        return True

    def add_event(self, event):
        self.session.add(event)
        self.session.commit()
        return event

