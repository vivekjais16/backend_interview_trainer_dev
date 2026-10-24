from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.models.user import Candidate
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserProfileUpdateRequest,
    UserResponse, AuthTokenResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["User Authentication & Accounts"])

@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register_account(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Registers a new candidate account with target role, target companies, and key skills."""
    try:
        return UserService.register_user(payload, db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")

@router.post("/login", response_model=AuthTokenResponse)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticates user credentials and issues an access token."""
    try:
        return UserService.authenticate_user(payload, db=db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
def get_current_profile(
    current_user: Candidate = Depends(get_current_user)
):
    """Retrieves authenticated candidate profile, requirements, and target metrics."""
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: UserProfileUpdateRequest,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates candidate target role, target companies, key skills, and experience preferences."""
    return UserService.update_profile(current_user, payload, db=db)
