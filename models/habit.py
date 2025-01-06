from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from models.base import Base


class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String())
    description = Column(String())
    repeat = Column(String())  # это Enum должен быть
    create_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='habits')
    events = relationship('Event', back_populates='habit')

    def __repr__(self):
        return f"id: {self.id}, name: {self.user_id}"


