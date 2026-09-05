"""AI用量配额"""
import logging
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, UsageLog
from auth import get_current_user
from schemas import UsageInfo
# 复用 billing.active_subscription：依赖其"已取消但未到期的订阅仍算权益有效"的约定
from .billing import active_subscription

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quota", tags=["配额"])

DAILY_LIMIT = 50  # 无订阅（免费版）的每日总限额


def get_user_daily_limit(user_id: int, db: Session):
    """返回该用户当日限额：付费套餐取 plan.daily_limit（None=不限），无订阅取默认 50。"""
    sub = active_subscription(db, user_id)
    if sub:
        return sub.plan.daily_limit  # None 表示不限量
    return DAILY_LIMIT


def check_quota(user_id: int, service_type: str, db: Session) -> bool:
    """检查今日是否超限，超限返回 False，未超限则记录用量并返回 True。

    付费不限量套餐（daily_limit=None）始终放行，仅记录用量。
    """
    limit = get_user_daily_limit(user_id, db)

    # 不限量套餐：仅记录用量，不限制
    if limit is None:
        db.add(UsageLog(user_id=user_id, service_type=service_type))
        db.commit()
        return True

    today = date.today()
    count = db.query(UsageLog).filter(
        UsageLog.user_id == user_id,
        func.date(UsageLog.created_at) == today,
    ).count()

    if count >= limit:
        logger.info("用户 %s 的 %s 配额已用完（%s/%s）", user_id, service_type, count, limit)
        return False

    db.add(UsageLog(user_id=user_id, service_type=service_type))
    db.commit()
    return True


@router.get("/usage", response_model=UsageInfo)
def my_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看当前用户今日用量与实际生效限额"""
    today = date.today()
    logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id,
        func.date(UsageLog.created_at) == today,
    ).all()

    result = UsageInfo(date=str(today), daily_limit=get_user_daily_limit(current_user.id, db))
    for log in logs:
        if log.service_type == "chat":
            result.chat += 1
        elif log.service_type == "contract":
            result.contract += 1
        elif log.service_type == "case_analysis":
            result.case_analysis += 1
        elif log.service_type == "document":
            result.document += 1
        elif log.service_type == "law_search":
            result.law_search += 1
    result.total = result.chat + result.contract + result.case_analysis + result.document + result.law_search
    return result
