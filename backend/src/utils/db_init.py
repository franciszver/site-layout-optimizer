"""
Database initialization script
"""
from sqlalchemy import create_engine, text
from models.site_models import Base
from config.settings import settings
import os


def init_database():
    """Initialize database with PostGIS extension"""
    # Create database URL
    if settings.database_url:
        database_url = settings.database_url
    else:
        database_url = (
            f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )
    
    engine = create_engine(database_url)
    
    # Create PostGIS extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(engine)
    
    print("Database initialized successfully!")
    print(f"PostGIS extension enabled")
    print(f"Tables created: {list(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_database()

