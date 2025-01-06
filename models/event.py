from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)
    execution_time = Column(DateTime, nullable=False, default=func.now())

    habit = relationship('Habit', back_populates='events')

    def __repr__(self):
        return f"id: {self.id}, name: {self.execution_time}"


