from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create engine — this is the actual connection to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# SessionLocal — each request gets its own session (database conversation)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base — all our SQLAlchemy models will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency function used by FastAPI endpoints.
    Gives each request a fresh database session,
    and closes it automatically when request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()