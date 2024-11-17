from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, challenges, labs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(labs.router, tags=["labs"])
