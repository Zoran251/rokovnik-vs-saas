from pydantic import BaseModel
from typing import Optional, List


class Answer(BaseModel):
    question_id: int
    option_indexes: List[int] = []
    other_text: Optional[str] = None


class PollSubmission(BaseModel):
    salon_name: str
    phone: str
    answers: List[Answer]
