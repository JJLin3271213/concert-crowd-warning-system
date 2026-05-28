from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 判断是否在云端环境（Railway / Docker 部署）
IS_PRODUCTION = (
    os.environ.get("RAILWAY_ENVIRONMENT") == "production"
    or os.environ.get("DEPLOYMENT", "") == "production"
    or os.path.exists("/.dockerenv")
)

if IS_PRODUCTION:
    # 云端使用 /app 目录（Docker 容器内可写，且已通过 COPY 预置数据）
    SQLALCHEMY_DATABASE_URL = "sqlite:////app/concert.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_size=10,
        max_overflow=20,
        pool_timeout=5,
        pool_pre_ping=True,
        pool_recycle=60
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