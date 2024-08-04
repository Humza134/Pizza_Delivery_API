from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from dotenv import load_dotenv, find_dotenv
import os

_:bool = load_dotenv(find_dotenv())
DB_URI = os.getenv('DB_URI', "")

engine = create_engine(DB_URI,echo=True)

Base = declarative_base()

# Session = sessionmaker()

Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()