from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("POSTGRES_DB_URL")
# db_url = f"postgresql://helixdb_a5py_user:u7c4zlt1LGha4nam8B9e3vleuOScb04t@dpg-d1kgj7emcj7s73cndrkg-a.singapore-postgres.render.com/helixdb_a5py"
print("Using PostgreSQL Database:", db_url)

DATABASE_URL = db_url

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
