from sqlalchemy import Column, DateTime, String, Integer, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Добавлено поле пароля

    # Отношение к модели Habit
    habits = relationship('Habit', back_populates='user')

    def __repr__(self):
        return f"id: {self.id}, name: {self.user_id}"





