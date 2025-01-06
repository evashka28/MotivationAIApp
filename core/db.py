from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.conf import DB_URL
from models.base import Base

db_url = DB_URL
engine = create_engine(db_url)

Session = sessionmaker(bind=engine)

session = Session()

Base.metadata.create_all(bind=engine)




