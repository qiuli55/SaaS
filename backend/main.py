"""Lexi 莱希后端入口：装配全部路由、CORS、访问日志中间件与静态前端托管。"""
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

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
from routers import user, cases, documents, files, clients, schedules, chat, contract, teams, firms, sms, invite, quota, billing, citation, law_search
from datetime import datetime
from models import User
from auth import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # 确保默认套餐存在（幂等）
    from routers.billing import ensure_plans
    with SessionLocal() as _db:
        ensure_plans(_db)
    yield


app = FastAPI(
    title="Lexi 莱希",
    description="面向小律所的轻量 AI 文书生成 + 案件管理系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS：不再使用 "*" + allow_credentials 的危险组合。
# 通过环境变量 CORS_ORIGINS 追加你的前端域名（逗号分隔）。
_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,https://qiuli55.top",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
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
app.include_router(contract.router)
app.include_router(teams.router)
app.include_router(firms.router)
app.include_router(sms.router)
app.include_router(invite.router)
app.include_router(quota.router)
app.include_router(billing.router)
app.include_router(citation.router)
app.include_router(law_search.router)


# 今日待办
from models import CaseDeadline, Case, Schedule
from sqlalchemy import func

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
    db = None
    if not request.url.path.startswith("/api/chat"):  # 避免记录心跳/轮询
        try:
            db = SessionLocal()
            ip = request.client.host if request.client else "unknown"
            log = VisitLog(ip=ip, path=request.url.path, method=request.method)
            db.add(log)
            db.commit()
        except Exception as e:
            # 日志记录失败不应影响主请求
            logger.warning("访问日志记录失败 path=%s: %s", request.url.path, e)
        finally:
            if db:
                db.close()
    return await call_next(request)


# 仅允许白名单内的管理员访问运维接口
ADMIN_USER_IDS = {
    int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()
}


@app.get("/api/admin/logs")
def view_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id not in ADMIN_USER_IDS:
        raise HTTPException(status_code=403, detail="无权限访问")
    try:
        logs = db.query(VisitLog).order_by(VisitLog.created_at.desc()).limit(limit).all()
        result = [{"ip": l.ip, "path": l.path, "method": l.method, "time": str(l.created_at)} for l in logs]
        # 汇总独立 IP
        ips = set(l.ip for l in logs)
        return {"count": len(logs), "unique_ips": list(ips), "logs": result}
    except Exception as e:
        logger.error("查询访问日志失败: %s", e)
        return {"error": "数据库不可用"}


@app.get("/")
def root():
    if FRONTEND_DIST.exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"name": "Lexi 莱希 API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
def health():
    """健康检查：探测数据库连通性"""
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_ok = True
        db.close()
    except Exception as e:
        logger.warning("健康检查数据库连接失败: %s", e)
    return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "disconnected"}


# 静态前端文件（部署时启用）——必须在所有 API 路由之后注册，
# 否则 SPA 兜底路由会按注册顺序抢先匹配，遮蔽 /api/health 等后定义的接口
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

        # 路径穿越防护：解析后必须仍位于 FRONTEND_DIST 之内
        dist_root = FRONTEND_DIST.resolve()
        file_path = (FRONTEND_DIST / path).resolve()
        if file_path != dist_root and dist_root not in file_path.parents:
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        if file_path.is_file() and path:
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
