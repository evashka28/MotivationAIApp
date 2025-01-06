from sqlalchemy.orm import Session


class BaseDAO:
    def __init__(self, session: Session):
        self.session = session

    def add(self, instance):
        """Добавить объект в сессию."""
        self.session.add(instance)
        self.session.commit()
        return instance

    def get_by_id(self, model, object_id):
        """Получить объект по ID."""
        return self.session.query(model).get(object_id)

    def delete(self, instance):
        """Удалить объект."""
        self.session.delete(instance)
        self.session.commit()
