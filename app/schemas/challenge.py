from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.challenge import ChallengeType, DifficultyLevel

class HintBase(BaseModel):
    content: str
    cost: int = 0

class HintCreate(HintBase):
    challenge_id: int

class Hint(HintBase):
    id: int
    challenge_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChallengeBase(BaseModel):
    title: str
    description: str
    category: ChallengeType
    difficulty: DifficultyLevel
    points: int = Field(..., ge=0)
    is_active: bool = True
    docker_image: Optional[str] = None
    port_mapping: Optional[str] = None

class ChallengeCreate(ChallengeBase):
    flag: str

class ChallengeUpdate(ChallengeBase):
    flag: Optional[str] = None

class Challenge(ChallengeBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    hints: List[Hint] = []

    class Config:
        orm_mode = True

class SubmissionBase(BaseModel):
    challenge_id: int
    submitted_flag: str

class SubmissionCreate(SubmissionBase):
    pass

class Submission(SubmissionBase):
    id: int
    user_id: int
    is_correct: bool
    points_awarded: int
    submitted_at: datetime

    class Config:
        orm_mode = True
