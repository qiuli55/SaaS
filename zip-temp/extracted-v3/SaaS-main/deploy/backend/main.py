import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 使用 python-dotenv 加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    # 兜底：手动解析 .env（python-dotenv 未安装时）
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

from database import engine, Base, SessionLocal
from sqlalchemy import text
from routers import user, cases, documents, files, clients, schedules, chat


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

# CORS — 智能匹配：localhost、局域网 IP、所有 cpolar 子域名
_CORS_REGEX = os.getenv(
    "CORS_REGEX",
    r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+)(:\d+)?|"
    r"https?://.+\.cpolar\.(top|cn)(:\d+)?"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=_CORS_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 注册路由
app.include_router(user.router)
app.include_router(cases.router)
app.include_router(documents.router)
app.include_router(files.router)
app.include_router(clients.router)
app.include_router(schedules.router)
app.include_router(chat.router)


# 静态前端文件（部署时启用）
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # API 请求已经走 router，这里只处理前端路由
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            return {"error": "not found"}
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


@app.get("/")
def root():
    if FRONTEND_DIST.exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"name": "法律AI助手 API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
def health():
    # 检查数据库连接
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_ok = True
        db.close()
    except Exception:
        pass
    return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "disconnected"}
