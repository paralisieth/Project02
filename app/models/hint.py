from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Hint(Base):
    __tablename__ = "hints"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    content = Column(Text, nullable=False)
    cost = Column(Integer, default=0)  # Point cost to view the hint
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    challenge = relationship("Challenge", back_populates="hints")
    hint_unlocks = relationship("HintUnlock", back_populates="hint")

class HintUnlock(Base):
    __tablename__ = "hint_unlocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hint_id = Column(Integer, ForeignKey("hints.id"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="hint_unlocks")
    hint = relationship("Hint", back_populates="hint_unlocks")
