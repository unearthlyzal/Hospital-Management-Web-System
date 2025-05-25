from models import Base
from db import engine

def cleanup_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(engine)
    print("Creating all tables...")
    Base.metadata.create_all(engine)
    print("Database reset complete!")

if __name__ == "__main__":
    cleanup_database() 