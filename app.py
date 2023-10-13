import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from models import Question as ModelQuestion, Base


app = FastAPI()
load_dotenv(".env")

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


class QuestionRequest(BaseModel):
    questions_num: int


async def fetch_question() -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://jservice.io/api/random?count=1")
        return response.json()


@app.post("/get_questions/")
async def get_questions(question_request: QuestionRequest) -> str:
    # Получение вопросов из внешнего API
    questions: list = []
    db: Session = SessionLocal()
    last_question: ModelQuestion = db.query(ModelQuestion).order_by(ModelQuestion.id.desc()).first()

    async with httpx.AsyncClient() as client:
        while len(questions) < question_request.questions_num:
            response: dict = await fetch_question()
            question_data: dict = response[0]

            # Проверка на уникальность вопроса
            existing_question: ModelQuestion = db.query(ModelQuestion).filter(ModelQuestion.question_text == question_data["question"]).first()
            if existing_question is None:
                db_question: ModelQuestion = ModelQuestion(
                    question_id=question_data["id"],
                    question_text=question_data["question"],
                    answer_text=question_data["answer"]
                )
                db.add(db_question)
                db.commit()
                db.refresh(db_question)
                questions.append(db_question)
            else:
                continue

    return last_question.question_text if last_question else ''


