from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 使用 SQLite 数据库（文件会自动创建在项目根目录）
SQLALCHEMY_DATABASE_URL = "sqlite:///./concert.db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 专用
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类（用于定义数据模型）
Base = declarative_base()

# 获取数据库会话（用于操作数据库）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()