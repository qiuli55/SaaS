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
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="法律AI助手",
    description="面向小律所的轻量 AI 文书生成 + 案件管理系统",
    version="1.0.0",
    lifespan=lifespan,
)

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
app.include_router(schedules.router)
app.include_router(chat.router)


# 访问日志中间件
from models import VisitLog
from fastapi import Request

@app.middleware("http")
async def visit_log_middleware(request: Request, call_next):
    if not request.url.path.startswith("/api/chat"):  # 避免记录心跳/轮询
        try:
            db = SessionLocal()
            ip = request.client.host if request.client else "unknown"
            log = VisitLog(ip=ip, path=request.url.path, method=request.method)
            db.add(log)
            db.commit()
            db.close()
        except:
            pass
    return await call_next(request)


@app.get("/api/admin/logs")
def view_logs(limit: int = 50):
    try:
        db = SessionLocal()
        logs = db.query(VisitLog).order_by(VisitLog.created_at.desc()).limit(limit).all()
        result = [{"ip": l.ip, "path": l.path, "method": l.method, "time": str(l.created_at)} for l in logs]
        # 汇总独立 IP
        ips = set(l.ip for l in logs)
        db.close()
        return {"count": len(logs), "unique_ips": list(ips), "logs": result}
    except:
        return {"error": "数据库不可用"}


# 静态前端文件（部署时启用）
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # 从路径中提取第一段，判断是否为 API 路径
        first = path.split("/")[0] if "/" in path else path
        if first in ("api", "docs", "openapi.json", "favicon.ico"):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        
        file_path = FRONTEND_DIST / path
        if file_path.is_file() and path:
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


@app.get("/")
def root():
    if FRONTEND_DIST.exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"name": "法律AI助手 API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
def health():
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_ok = True
        db.close()
    except Exception:
        pass
    return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "disconnected"}
