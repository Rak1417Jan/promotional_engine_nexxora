"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.auth import (
    OperatorRegister, UserRegister, UserLogin, TokenResponse, UserResponse,
    PasswordResetRequest, PasswordReset, PasswordChange
)
from app.services.auth_service import AuthService
from app.models.operator_user import OperatorUser
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> OperatorUser:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = AuthService.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/register-operator", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_operator(
    data: OperatorRegister,
    db: Session = Depends(get_db)
):
    """Register a new operator and first owner user (Phase 1 onboarding)."""
    try:
        _, user = AuthService.create_operator_and_owner(
            db=db,
            name=data.name,
            domain_url=data.domain_url,
            contact_email=data.contact_email,
            password=data.password
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error registering operator", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering operator"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    operator_id: int,
    db: Session = Depends(get_db)
):
    """Register a new user for an existing operator (requires operator_id)."""
    try:
        user = AuthService.create_user(
            db=db,
            operator_id=operator_id,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error registering user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id), "operator_id": user.operator_id})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id), "operator_id": user.operator_id})
    
    # Create session
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    AuthService.create_session(
        db=db,
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    logger.info("User logged in", user_id=user.id, email=user.email)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    payload = AuthService.verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = AuthService.get_user_by_id(db, int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id), "operator_id": user.operator_id})
    new_refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id), "operator_id": user.operator_id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: OperatorUser = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/password-reset-request")
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset (sends email)"""
    user = AuthService.get_user_by_email(db, request_data.email)
    
    # Always return success to prevent email enumeration
    if user:
        # TODO: Send password reset email
        logger.info("Password reset requested", email=request_data.email)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    # TODO: Verify reset token and update password
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not yet implemented"
    )


@router.post("/password-change")
async def change_password(
    password_data: PasswordChange,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password"""
    # Verify current password
    if not AuthService.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = AuthService.hash_password(password_data.new_password)
    db.commit()
    
    logger.info("Password changed", user_id=current_user.id)
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout (invalidate session)"""
    # TODO: Invalidate session in database
    logger.info("User logged out", user_id=current_user.id)
    return {"message": "Logged out successfully"}
