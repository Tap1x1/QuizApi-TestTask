from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer)
    question_text = Column(String)
    answer_text = Column(String)
    created_at = Column(DateTime, default=datetime.now)