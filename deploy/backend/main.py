import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
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

from database import engine, Base, SessionLocal, get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from routers import user, cases, documents, files, clients, schedules, chat
from datetime import datetime
from models import User
from auth import get_current_user


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


# 今日待办
from models import CaseDeadline, Case, Schedule
from sqlalchemy import and_

@app.get("/api/today")
def today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """今日待办：审限 + 日程"""
    now = datetime.now()
    today = now.date()

    # 未完成的审限（按紧迫度排序）
    deadlines = db.query(CaseDeadline).join(Case).filter(
        CaseDeadline.user_id == current_user.id,
        CaseDeadline.is_done == False,
    ).all()

    overdue = []
    today_dl = []
    upcoming = []
    for d in deadlines:
        days_left = (d.deadline_date.date() - today).days if d.deadline_date else 999
        item = {
            "id": d.id, "case_id": d.case_id, "case_name": d.case.plaintiff + " vs " + d.case.defendant if d.case else "未知案件",
            "deadline_type": d.deadline_type, "deadline_date": str(d.deadline_date)[:10] if d.deadline_date else "",
            "days_left": days_left, "notes": d.notes,
        }
        if days_left < 0:
            overdue.append(item)
        elif days_left == 0:
            today_dl.append(item)
        elif days_left <= 3:
            upcoming.append(item)

    # 今日日程
    schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        func.date(Schedule.event_date) == today,
    ).all()
    today_schedules = [{"id": s.id, "event_type": s.event_type, "event_date": str(s.event_date)[:16], "notes": s.notes} for s in schedules]

    # 进行中案件数
    active_cases = db.query(Case).filter(Case.user_id == current_user.id, Case.status == "进行中").count()

    return {
        "overdue": overdue,
        "today": today_dl,
        "upcoming": upcoming,
        "schedules": today_schedules,
        "active_cases": active_cases,
        "urgent_count": len(overdue) + len(today_dl),
        "date": str(today),
    }


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
