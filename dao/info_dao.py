'''from core.db import engine, Session
from models.user import Info

db = Session(autoflush=False, bind=engine)


class InfoDAO:
    def add_info(self, user_id, username, question, answer, chain_trace):
        info = Info(user_id=user_id, username=username, question=question, answer=answer, chain_trace=chain_trace)
        db.add(info)
        db.commit()

    def get_user_history(self, user_id):
        history = db.query(Info).filter(Info.user_id == 'user_id').all()'''


