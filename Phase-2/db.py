from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up SQLAlchemy engine and session
engine = create_engine(os.getenv("SQLSERVER_CONN"), echo=True, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Create a db instance to be imported by other modules
db = SessionLocal()

# Export the session instance
__all__ = ['db', 'engine', 'Base', 'SessionLocal']
