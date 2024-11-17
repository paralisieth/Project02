from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class ChallengeType(str, enum.Enum):
    WEB = "web"
    CRYPTO = "crypto"
    FORENSICS = "forensics"
    REVERSE = "reverse"
    PWN = "pwn"
    MISC = "misc"

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    INSANE = "insane"

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ChallengeType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    points = Column(Integer, nullable=False)
    flag = Column(String(255), nullable=False)  # Store hashed flag
    is_active = Column(Boolean, default=True)
    docker_image = Column(String(255), nullable=True)  # For containerized challenges
    port_mapping = Column(String(20), nullable=True)  # For network services
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User", back_populates="created_challenges")
    submissions = relationship("Submission", back_populates="challenge")
    hints = relationship("Hint", back_populates="challenge")
    labs = relationship("Lab", back_populates="challenge")
