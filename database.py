from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# SQLALCHEMY_DATABASE_URL = "sqlite:///./medicines.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
DB_HOST = "localhost"
POSTGRES_DB_URL = f"postgresql://postgres:root@{DB_HOST}:5432/helixDB"
print("Using PostgreSQL Database:", POSTGRES_DB_URL)

DATABASE_URL = POSTGRES_DB_URL

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=30,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Active_DB = 0
