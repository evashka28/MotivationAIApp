from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from models import Base


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    max_experience = Column(Integer, default=50)
    current_health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    avatar = Column(String)  # Можно хранить ссылку на изображение

    user = relationship('User', back_populates='character')

    def __repr__(self):
        return f"Character(id: {self.id}, name: {self.name}, level: {self.level}, experience: {self.experience})"