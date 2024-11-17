from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from passlib.hash import bcrypt

from app.models.challenge import Challenge, ChallengeType, DifficultyLevel
from app.models.submission import Submission
from app.models.hint import Hint, HintUnlock
from app.models.user import User
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate, HintCreate

def create_challenge(db: Session, challenge: ChallengeCreate, creator_id: int) -> Challenge:
    # Hash the flag before storing
    hashed_flag = bcrypt.hash(challenge.flag)
    db_challenge = Challenge(
        **challenge.dict(exclude={'flag'}),
        flag=hashed_flag,
        creator_id=creator_id
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_challenge(db: Session, challenge_id: int) -> Optional[Challenge]:
    return db.query(Challenge).filter(Challenge.id == challenge_id).first()

def get_challenges(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[ChallengeType] = None,
    difficulty: Optional[DifficultyLevel] = None,
    is_active: bool = True
) -> List[Challenge]:
    query = db.query(Challenge).filter(Challenge.is_active == is_active)
    
    if category:
        query = query.filter(Challenge.category == category)
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)
    
    return query.order_by(desc(Challenge.created_at)).offset(skip).limit(limit).all()

def update_challenge(
    db: Session,
    challenge_id: int,
    challenge_update: ChallengeUpdate
) -> Optional[Challenge]:
    db_challenge = get_challenge(db, challenge_id)
    if not db_challenge:
        return None
    
    update_data = challenge_update.dict(exclude_unset=True)
    if 'flag' in update_data:
        update_data['flag'] = bcrypt.hash(update_data['flag'])
    
    for field, value in update_data.items():
        setattr(db_challenge, field, value)
    
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def delete_challenge(db: Session, challenge_id: int) -> bool:
    db_challenge = get_challenge(db, challenge_id)
    if not db_challenge:
        return False
    db.delete(db_challenge)
    db.commit()
    return True

def create_hint(db: Session, hint: HintCreate) -> Hint:
    db_hint = Hint(**hint.dict())
    db.add(db_hint)
    db.commit()
    db.refresh(db_hint)
    return db_hint

def get_challenge_hints(db: Session, challenge_id: int, user_id: Optional[int] = None) -> List[Hint]:
    query = db.query(Hint).filter(Hint.challenge_id == challenge_id)
    if user_id:
        # Only return hints that the user has unlocked
        query = query.join(HintUnlock).filter(HintUnlock.user_id == user_id)
    return query.all()

def unlock_hint(db: Session, hint_id: int, user_id: int) -> Optional[HintUnlock]:
    # Check if user has enough points and hasn't already unlocked the hint
    hint = db.query(Hint).filter(Hint.id == hint_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not hint or not user:
        return None
    
    # Check if already unlocked
    existing_unlock = db.query(HintUnlock).filter(
        HintUnlock.hint_id == hint_id,
        HintUnlock.user_id == user_id
    ).first()
    
    if existing_unlock:
        return existing_unlock
    
    # Check if user has enough points
    if user.points < hint.cost:
        return None
    
    # Create hint unlock and deduct points
    unlock = HintUnlock(hint_id=hint_id, user_id=user_id)
    user.points -= hint.cost
    
    db.add(unlock)
    db.commit()
    db.refresh(unlock)
    return unlock

def submit_flag(db: Session, challenge_id: int, user_id: int, submitted_flag: str) -> Submission:
    challenge = get_challenge(db, challenge_id)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not challenge or not user:
        raise ValueError("Challenge or user not found")
    
    # Check if user has already solved this challenge
    existing_correct = db.query(Submission).filter(
        Submission.challenge_id == challenge_id,
        Submission.user_id == user_id,
        Submission.is_correct == True
    ).first()
    
    if existing_correct:
        return existing_correct
    
    # Verify flag
    is_correct = bcrypt.verify(submitted_flag, challenge.flag)
    points_awarded = challenge.points if is_correct else 0
    
    # Create submission
    submission = Submission(
        challenge_id=challenge_id,
        user_id=user_id,
        submitted_flag=bcrypt.hash(submitted_flag),  # Hash submitted flag for security
        is_correct=is_correct,
        points_awarded=points_awarded
    )
    
    # Update user points if correct
    if is_correct:
        user.points += points_awarded
        # Update user rank (simplified version - could be more sophisticated)
        higher_ranked = db.query(User).filter(User.points > user.points).count()
        user.rank = higher_ranked + 1
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
