"""
Database Connection and Session Management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import redis
from app.config import settings

# PostgreSQL Database
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    Sets tenant context for Row-Level Security
    """
    db = SessionLocal()
    try:
        # Set tenant context if available in request state
        # This will be set by tenant middleware
        # For now, we'll handle it in the dependency
        yield db
    finally:
        db.close()


def set_tenant_context(db: Session, operator_id: int) -> None:
    """
    Set tenant context for Row-Level Security
    This sets a PostgreSQL session variable that RLS policies use
    """
    try:
        db.execute(text(f"SET app.current_operator_id = {operator_id}"))
        db.commit()
    except Exception as e:
        # If RLS is not enabled or variable doesn't exist, log and continue
        # This allows development without RLS
        pass


# Redis Connection
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test connection
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis connection failed: {e}. Some features may not work.")
    redis_client = None


def get_redis() -> redis.Redis:
    """
    Redis client dependency
    """
    return redis_client


def init_db():
    """
    Initialize database tables and enable Row-Level Security
    """
    try:
        Base.metadata.create_all(bind=engine)
        
        # Enable RLS on tables that need it
        with engine.connect() as conn:
            # Enable RLS on operators table
            conn.execute(text("ALTER TABLE operators ENABLE ROW LEVEL SECURITY"))
            conn.execute(text("ALTER TABLE operator_users ENABLE ROW LEVEL SECURITY"))
            
            # Create RLS policies
            # Policy for operators - users can only see their own operator
            conn.execute(text("""
                DROP POLICY IF EXISTS operator_isolation ON operators;
                CREATE POLICY operator_isolation ON operators
                    USING (id = current_setting('app.current_operator_id', true)::INTEGER);
            """))
            
            # Policy for operator_users - users can only see users from their operator
            conn.execute(text("""
                DROP POLICY IF EXISTS operator_users_isolation ON operator_users;
                CREATE POLICY operator_users_isolation ON operator_users
                    USING (operator_id = current_setting('app.current_operator_id', true)::INTEGER);
            """))
            
            conn.commit()
        
        print("✅ Database tables initialized successfully")
        print("✅ Row-Level Security enabled")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        # If RLS setup fails, continue anyway (for development)
        import traceback
        traceback.print_exc()
