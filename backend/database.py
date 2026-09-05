"""数据库连接与会话管理：SQLAlchemy engine / SessionLocal / FastAPI 依赖 get_db。"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legal_ai.db")

connect_args = {}
if "sqlite" in DATABASE_URL:
    # check_same_thread=False: 允许跨线程使用同一连接（FastAPI 多线程）
    # timeout: 写锁等待毫秒，避免并发 "database is locked"
    # 应用层再开 WAL 进一步提升并发读能力
    connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # 显式连接池：避免每个请求反复建连，限制峰值连接数
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,   # 借用连接前探活，自动剔除失效连接
    pool_recycle=1800,    # 30 分钟回收，规避 SQLite 长连接潜在问题
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        # SQLite 开启 WAL 模式，提升并发读写吞吐
        if "sqlite" in DATABASE_URL:
            db.execute(text("PRAGMA journal_mode=WAL"))
        yield db
    finally:
        db.close()
