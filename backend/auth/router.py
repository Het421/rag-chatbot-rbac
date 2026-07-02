from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth.models import User
from auth.schemas import LoginRequest, TokenResponse
from auth.utils import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Step 1: Find user by employee_id
    user = db.query(User).filter(User.employee_id == request.employee_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID or password"
        )

    # Step 2: Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated"
        )

    # Step 3: Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID or password"
        )

    # Step 4: Create JWT token
    access_token = create_access_token(
        data={"sub": user.employee_id, "role": user.role}
    )

    # Step 5: Return token + basic user info
    return TokenResponse(
        access_token=access_token,
        role=user.role,
        full_name=user.full_name
    )