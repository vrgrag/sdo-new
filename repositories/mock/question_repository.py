from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from schemas import QuestionResponse, QuestionCreate, QuestionUpdate
from schemas import AnswerResponse, AnswerCreate
from models.questions import Question
from models.answers import Answer


class QuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_response(self, question: Question, answers: List[Answer] = None) -> QuestionResponse:
        """Преобразует модель Question в QuestionResponse"""
        answer_responses = []
        if answers:
            answer_responses = [
                AnswerResponse(
                    id=a.id,
                    answer_text=a.answer_text,
                    is_correct=a.is_correct,
                    question_id=a.question_id,
                )
                for a in answers
            ]
        else:
            # Если ответы не переданы, получаем их из базы
            # Это не оптимально, лучше передавать всегда
            pass
        
        return QuestionResponse(
            id=question.id,
            question_text=question.question_text,
            question_type=question.question_type,
            test_id=question.test_id,
            answers=answer_responses,
        )

    async def get_all(
        self,
        test_id: Optional[int] = None
    ) -> List[QuestionResponse]:
        """Получить все вопросы, опционально фильтровать по тесту"""
        stmt = select(Question)
        
        if test_id is not None:
            stmt = stmt.where(Question.test_id == test_id)
        
        res = await self.db.execute(stmt)
        questions = res.scalars().all()
        
        # Получаем ответы для каждого вопроса
        result = []
        for q in questions:
            stmt_answers = select(Answer).where(Answer.question_id == q.id)
            res_answers = await self.db.execute(stmt_answers)
            answers = res_answers.scalars().all()
            result.append(self._to_response(q, list(answers)))
        
        return result

    async def get_by_id(self, question_id: int) -> Optional[QuestionResponse]:
        """Получить вопрос по ID"""
        question = await self.db.get(Question, question_id)
        if not question:
            return None
        
        # Получаем ответы
        stmt_answers = select(Answer).where(Answer.question_id == question_id)
        res_answers = await self.db.execute(stmt_answers)
        answers = res_answers.scalars().all()
        
        return self._to_response(question, list(answers))

    async def create(self, question: QuestionCreate) -> QuestionResponse:
        """Создать новый вопрос с ответами"""
        question_obj = Question(
            question_text=question.question_text,
            question_type=question.question_type,
            test_id=question.test_id,
        )
        self.db.add(question_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        await self.db.refresh(question_obj)
        
        # Создаем ответы, если они есть
        answers_list = []
        for answer_data in question.answers:
            answer_obj = Answer(
                answer_text=answer_data.answer_text,
                is_correct=answer_data.is_correct,
                question_id=question_obj.id,
            )
            self.db.add(answer_obj)
            answers_list.append(answer_obj)
        
        if answers_list:
            try:
                await self.db.commit()
            except IntegrityError:
                await self.db.rollback()
                raise
            for a in answers_list:
                await self.db.refresh(a)
        
        return self._to_response(question_obj, answers_list)

    async def update(self, question_id: int, question_data: QuestionUpdate) -> Optional[QuestionResponse]:
        """Обновить вопрос"""
        question = await self.db.get(Question, question_id)
        if not question:
            return None
        
        update_data = question_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(question, key, value)
        
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise
        
        await self.db.refresh(question)
        
        # Получаем ответы
        stmt_answers = select(Answer).where(Answer.question_id == question_id)
        res_answers = await self.db.execute(stmt_answers)
        answers = res_answers.scalars().all()
        
        return self._to_response(question, list(answers))

    async def delete(self, question_id: int) -> bool:
        """Удалить вопрос (ответы удалятся каскадно)"""
        question = await self.db.get(Question, question_id)
        if not question:
            return False
        await self.db.delete(question)
        await self.db.commit()
        return True

