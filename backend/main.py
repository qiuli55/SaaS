import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 加载 .env 文件（必须在 import routers 之前, 因为 routers 在模块级别读环境变量）
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

from database import engine, Base
from routers import user, cases, documents, files, clients


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建所有表
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="法律AI助手",
    description="面向小律所的轻量 AI 文书生成 + 案件管理系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user.router)
app.include_router(cases.router)
app.include_router(documents.router)
app.include_router(files.router)
app.include_router(clients.router)


@app.get("/")
def root():
    return {"name": "法律AI助手 API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
