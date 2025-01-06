from sqlalchemy.orm import Session
from models.user import User
from dao.base_dao import BaseDAO

class UserDAO(BaseDAO):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_username(self, username: str):
        """Получить пользователя по имени."""
        return self.session.query(User).filter_by(username=username).first()

    def get_all_users(self):
        """Получить всех пользователей."""
        return self.session.query(User).all()
