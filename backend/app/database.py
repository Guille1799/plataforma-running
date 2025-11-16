import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Get database URL from environment variable
# Falls back to SQLite for backwards compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./runcoach.db")

# Create SQLAlchemy engine
# For PostgreSQL: use NullPool to avoid connection issues
# For SQLite: use check_same_thread=False
if "postgresql" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Better for containerized environments
        echo=False  # Set to True for SQL debugging
    )
else:
    # SQLite fallback for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# Create SessionLocal class for database sessions
# Each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
# All database models will inherit from this
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session.
    
    Yields:
        Database session that will be closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()