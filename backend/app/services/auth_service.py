"""
Authentication Service
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from app.config import settings
from app.models.operator_user import OperatorUser
from app.models.user_session import UserSession
from app.models.operator import Operator
from app.utils.logger import logger
import hashlib

# bcrypt has a 72-byte limit; truncate to avoid error
BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    """Encode password to bytes and truncate to bcrypt's 72-byte limit."""
    raw = password.encode("utf-8")
    return raw[:BCRYPT_MAX_PASSWORD_BYTES] if len(raw) > BCRYPT_MAX_PASSWORD_BYTES else raw


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password (passwords longer than 72 bytes are truncated)."""
        pw_bytes = _password_bytes(password)
        return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        pw_bytes = _password_bytes(plain_password)
        return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def create_user(
        db: Session,
        operator_id: int,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "analyst"
    ) -> OperatorUser:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(OperatorUser).filter(
            OperatorUser.operator_id == operator_id,
            OperatorUser.email == email,
            OperatorUser.deleted_at.is_(None)
        ).first()
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Verify operator exists
        operator = db.query(Operator).filter(Operator.id == operator_id).first()
        if not operator:
            raise ValueError("Operator not found")
        
        # Create user
        user = OperatorUser(
            operator_id=operator_id,
            email=email,
            password_hash=AuthService.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info("User created", user_id=user.id, email=email, operator_id=operator_id)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[OperatorUser]:
        """Authenticate a user"""
        user = db.query(OperatorUser).filter(
            OperatorUser.email == email,
            OperatorUser.deleted_at.is_(None)
        ).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_session(
        db: Session,
        user: OperatorUser,
        access_token: str,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a user session"""
        session = UserSession(
            user_id=user.id,
            operator_id=user.operator_id,
            token_hash=AuthService.hash_token(access_token),
            refresh_token_hash=AuthService.hash_token(refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[OperatorUser]:
        """Get user by ID"""
        return db.query(OperatorUser).filter(
            OperatorUser.id == user_id,
            OperatorUser.deleted_at.is_(None)
        ).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[OperatorUser]:
        """Get user by email"""
        return db.query(OperatorUser).filter(
            OperatorUser.email == email,
            OperatorUser.deleted_at.is_(None)
        ).first()

    @staticmethod
    def create_operator_and_owner(
        db: Session,
        name: str,
        domain_url: str,
        contact_email: str,
        password: str
    ) -> tuple:
        """Create operator and first owner user. Returns (operator, user)."""
        existing_op = db.query(Operator).filter(Operator.domain_url == domain_url).first()
        if existing_op:
            raise ValueError("Operator with this domain already exists")
        existing_user = db.query(OperatorUser).filter(
            OperatorUser.email == contact_email,
            OperatorUser.deleted_at.is_(None)
        ).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        operator = Operator(
            name=name,
            domain_url=domain_url,
            contact_email=contact_email
        )
        db.add(operator)
        db.flush()
        user = OperatorUser(
            operator_id=operator.id,
            email=contact_email,
            password_hash=AuthService.hash_password(password),
            first_name=name.split()[0] if name else None,
            last_name=" ".join(name.split()[1:]) if name and len(name.split()) > 1 else None,
            role="owner"
        )
        db.add(user)
        db.commit()
        db.refresh(operator)
        db.refresh(user)
        logger.info("Operator and owner created", operator_id=operator.id, email=contact_email)
        return operator, user
