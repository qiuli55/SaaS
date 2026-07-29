"""AI用量配额"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, UsageLog
from auth import get_current_user
from schemas import UsageInfo

router = APIRouter(prefix="/api/quota", tags=["配额"])

DAILY_LIMIT = 50  # 每人每天总限额


def check_quota(user_id: int, service_type: str, db: Session) -> bool:
    """检查今日是否超限，超限返回 False，未超限则记录并返回 True"""
    today = date.today()
    count = db.query(UsageLog).filter(
        UsageLog.user_id == user_id,
        func.date(UsageLog.created_at) == today,
    ).count()

    if count >= DAILY_LIMIT:
        return False

    db.add(UsageLog(user_id=user_id, service_type=service_type))
    db.commit()
    return True


@router.get("/usage", response_model=UsageInfo)
def my_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看当前用户今日用量"""
    today = date.today()
    logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id,
        func.date(UsageLog.created_at) == today,
    ).all()

    result = UsageInfo(date=str(today), daily_limit=DAILY_LIMIT)
    for log in logs:
        if log.service_type == "chat":
            result.chat += 1
        elif log.service_type == "contract":
            result.contract += 1
        elif log.service_type == "case_analysis":
            result.case_analysis += 1
        elif log.service_type == "document":
            result.document += 1
    result.total = result.chat + result.contract + result.case_analysis + result.document
    return result
