from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 判断是否在 Railway 云端环境
IS_PRODUCTION = os.environ.get("RAILWAY_ENVIRONMENT") == "production"

if IS_PRODUCTION:
    # 云端使用 /tmp 目录（可写临时目录）
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/concert.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_size=1,
        max_overflow=0,
        pool_timeout=30,
        pool_pre_ping=True
    )
else:
    # 本地开发
    SQLALCHEMY_DATABASE_URL = "sqlite:///./concert.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()