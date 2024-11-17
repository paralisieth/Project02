from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models.challenge import ChallengeType, DifficultyLevel
from app.models.user import User
from app.schemas.challenge import (
    Challenge,
    ChallengeCreate,
    ChallengeUpdate,
    Hint,
    HintCreate,
    Submission,
    SubmissionCreate
)

router = APIRouter()

@router.post("/challenges/", response_model=Challenge)
def create_challenge(
    *,
    db: Session = Depends(deps.get_db),
    challenge_in: ChallengeCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Create a new challenge (superuser only).
    """
    challenge = crud.challenge.create_challenge(db, challenge_in, current_user.id)
    return challenge

@router.get("/challenges/", response_model=List[Challenge])
def list_challenges(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[ChallengeType] = None,
    difficulty: Optional[DifficultyLevel] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    List all active challenges with optional filtering.
    """
    challenges = crud.challenge.get_challenges(
        db,
        skip=skip,
        limit=limit,
        category=category,
        difficulty=difficulty
    )
    return challenges

@router.get("/challenges/{challenge_id}", response_model=Challenge)
def get_challenge(
    challenge_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a specific challenge by ID.
    """
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge

@router.put("/challenges/{challenge_id}", response_model=Challenge)
def update_challenge(
    *,
    db: Session = Depends(deps.get_db),
    challenge_id: int,
    challenge_in: ChallengeUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Update a challenge (superuser only).
    """
    challenge = crud.challenge.update_challenge(db, challenge_id, challenge_in)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge

@router.delete("/challenges/{challenge_id}")
def delete_challenge(
    *,
    db: Session = Depends(deps.get_db),
    challenge_id: int,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Delete a challenge (superuser only).
    """
    success = crud.challenge.delete_challenge(db, challenge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {"message": "Challenge deleted successfully"}

@router.post("/challenges/{challenge_id}/submit", response_model=Submission)
def submit_challenge_flag(
    *,
    db: Session = Depends(deps.get_db),
    challenge_id: int,
    submission: SubmissionCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Submit a flag for a challenge.
    """
    try:
        result = crud.challenge.submit_flag(
            db,
            challenge_id=challenge_id,
            user_id=current_user.id,
            submitted_flag=submission.submitted_flag
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/challenges/{challenge_id}/hints", response_model=Hint)
def create_challenge_hint(
    *,
    db: Session = Depends(deps.get_db),
    challenge_id: int,
    hint_in: HintCreate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Add a hint to a challenge (superuser only).
    """
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    hint = crud.challenge.create_hint(db, hint_in)
    return hint

@router.get("/challenges/{challenge_id}/hints", response_model=List[Hint])
def get_challenge_hints(
    challenge_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all available hints for a challenge (only unlocked hints for regular users).
    """
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Superusers can see all hints
    user_id = None if current_user.is_superuser else current_user.id
    hints = crud.challenge.get_challenge_hints(db, challenge_id, user_id)
    return hints

@router.post("/hints/{hint_id}/unlock", response_model=Hint)
def unlock_challenge_hint(
    hint_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Unlock a hint by spending points.
    """
    unlock = crud.challenge.unlock_hint(db, hint_id, current_user.id)
    if not unlock:
        raise HTTPException(
            status_code=400,
            detail="Hint not found or insufficient points to unlock"
        )
    return unlock.hint
