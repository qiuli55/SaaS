"""订阅收费系统（套餐 / 订单 / 订阅 / 模拟支付）

当前支付为 mock（点"支付"即成功），后续接微信/支付宝只需替换 pay 接口内部实现，
并把 pay_method 改为对应渠道、补充异步回调即可，接口契约保持不变。
"""
import secrets
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import Plan, Subscription, Order, User, UsageLog
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/billing", tags=["收费"])


# 默认套餐（集中配置，改这里即可调整档位/价格/额度）
PLANS = [
    {
        "code": "free",
        "name": "免费版",
        "price_monthly": Decimal("0"),
        "price_yearly": Decimal("0"),
        "daily_limit": 50,
        "features": [
            "合同审查 / 案件分析 / 文书生成 / AI 对话",
            "每日 50 次 AI 调用",
            "单设备使用",
        ],
    },
    {
        "code": "basic",
        "name": "基础版",
        "price_monthly": Decimal("39"),
        "price_yearly": Decimal("390"),
        "daily_limit": 500,
        "features": [
            "包含免费版全部功能",
            "每日 500 次 AI 调用",
            "批量生成文书",
            "客户通讯录不限量",
        ],
    },
    {
        "code": "pro",
        "name": "专业版",
        "price_monthly": Decimal("99"),
        "price_yearly": Decimal("990"),
        "daily_limit": None,  # 不限量
        "features": [
            "包含基础版全部功能",
            "AI 调用不限量",
            "数据导出 / 优先响应",
            "团队协作增强",
        ],
    },
]


def ensure_plans(db: Session):
    """幂等写入默认套餐，只在有新增时提交，避免重复创建。"""
    added = 0
    for idx, p in enumerate(PLANS):
        if not db.query(Plan).filter(Plan.code == p["code"]).first():
            db.add(
                Plan(
                    code=p["code"],
                    name=p["name"],
                    price_monthly=p["price_monthly"],
                    price_yearly=p["price_yearly"],
                    daily_limit=p["daily_limit"],
                    features=p["features"],
                    sort_order=idx,
                )
            )
            added += 1
    if added:
        db.commit()
        logger.info("初始化默认套餐 %s 个", added)


# ========== 请求模型 ==========
class OrderCreate(BaseModel):
    plan_code: str
    period: str = Field(default="monthly", pattern="^(monthly|yearly)$")


# ========== 工具 ==========
def _gen_order_no() -> str:
    """生成全局唯一订单号：LX + 时间戳 + 8 位随机 hex。"""
    return "LX" + datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(4).upper()


def active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """返回用户当前权益有效的订阅；没有则返回 None。

    取消订阅只是停掉续费：已取消但未到期的订阅在周期内仍保留套餐权益
    （end_at 过后自然失效）。优先返回 active 订阅，其次取到期最晚的已取消订阅。
    被 quota.get_user_daily_limit 复用，改动过滤条件需同步该处语义。
    """
    now = datetime.now()
    q = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        (Subscription.end_at.is_(None)) | (Subscription.end_at > now),
    )
    sub = q.filter(Subscription.status == "active").first()
    if sub:
        return sub
    return (
        q.filter(Subscription.status == "cancelled")
        .order_by(Subscription.end_at.desc())
        .first()
    )


def _today_usage(db: Session, user_id: int) -> int:
    """统计用户今日 AI 调用总次数。"""
    today = datetime.now().date()
    return (
        db.query(UsageLog)
        .filter(UsageLog.user_id == user_id, func.date(UsageLog.created_at) == today)
        .count()
    )


def _serialize_plan(plan: Plan) -> dict:
    """套餐对象转响应 dict（daily_limit=None 表示不限量）。"""
    return {
        "code": plan.code,
        "name": plan.name,
        "price_monthly": float(plan.price_monthly),
        "price_yearly": float(plan.price_yearly),
        "daily_limit": plan.daily_limit,  # None = 不限
        "features": plan.features or [],
    }


# ========== 接口 ==========
@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    """套餐列表（含模拟支付说明）"""
    ensure_plans(db)
    plans = db.query(Plan).filter(Plan.is_active.is_(True)).order_by(Plan.sort_order).all()
    return {
        "plans": [_serialize_plan(p) for p in plans],
        "pay_method": "mock",  # 当前为模拟支付
    }


@router.post("/orders")
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建购买订单（mock 支付，直接生成待支付订单）"""
    ensure_plans(db)
    plan = db.query(Plan).filter(Plan.code == body.plan_code, Plan.is_active.is_(True)).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")
    if plan.code == "free":
        raise HTTPException(status_code=400, detail="免费版无需购买")

    amount = plan.price_yearly if body.period == "yearly" else plan.price_monthly
    order_no = _gen_order_no()
    order = Order(
        order_no=order_no,
        user_id=current_user.id,
        plan_id=plan.id,
        plan_code=plan.code,
        plan_name=plan.name,
        amount=amount,
        period=body.period,
        status="pending",
        pay_method="mock",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    logger.info("用户 %s 创建订单 %s plan=%s period=%s amount=%s",
                current_user.id, order_no, plan.code, body.period, amount)
    return {
        "order_no": order.order_no,
        "plan_code": order.plan_code,
        "plan_name": order.plan_name,
        "amount": float(order.amount),
        "period": order.period,
        "status": order.status,
        "created_at": str(order.created_at),
    }


@router.post("/orders/{order_no}/pay")
def mock_pay(
    order_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """模拟支付：标记订单已支付并激活对应订阅。"""
    order = (
        db.query(Order)
        .filter(Order.order_no == order_no, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status == "paid":
        return {"status": "paid", "message": "该订单已支付"}

    order.status = "paid"
    order.paid_at = datetime.now()

    # 结束当前生效中的订阅，开新订阅（避免叠加）
    old = active_subscription(db, current_user.id)
    if old:
        old.status = "cancelled"

    days = 365 if order.period == "yearly" else 30
    sub = Subscription(
        user_id=current_user.id,
        plan_id=order.plan_id,
        plan_code=order.plan_code,
        status="active",
        period=order.period,
        start_at=datetime.now(),
        end_at=datetime.now() + timedelta(days=days),
    )
    db.add(sub)
    db.commit()
    logger.info("订单 %s 支付成功，用户 %s 开通 %s（%s），到期 %s",
                order_no, current_user.id, order.plan_code, order.period, sub.end_at)
    return {
        "status": "paid",
        "message": f"支付成功，已开通{order.plan_name}（{order.period}）",
        "plan_code": order.plan_code,
        "end_at": str(sub.end_at),
    }


@router.get("/subscription/current")
def current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """当前生效订阅 + 用量概览"""
    sub = active_subscription(db, current_user.id)
    if not sub:
        return {
            "plan": _serialize_plan(
                db.query(Plan).filter(Plan.code == "free").first()
            ),
            "is_paid": False,
            "status": "free",
            "end_at": None,
            "today_usage": _today_usage(db, current_user.id),
            "daily_limit": 50,
        }
    plan = sub.plan
    limit = plan.daily_limit
    return {
        "plan": _serialize_plan(plan),
        "is_paid": True,
        "status": sub.status,
        "period": sub.period,
        "start_at": str(sub.start_at),
        "end_at": str(sub.end_at) if sub.end_at else None,
        "today_usage": _today_usage(db, current_user.id),
        "daily_limit": limit,  # None = 不限
    }


@router.get("/orders")
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的订单列表"""
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return {
        "orders": [
            {
                "order_no": o.order_no,
                "plan_name": o.plan_name,
                "amount": float(o.amount),
                "period": o.period,
                "status": o.status,
                "pay_method": o.pay_method,
                "paid_at": str(o.paid_at) if o.paid_at else None,
                "created_at": str(o.created_at),
            }
            for o in orders
        ]
    }


@router.post("/subscription/cancel")
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消当前订阅（停续费，本周期内权益保留，到期自动降级为免费版）"""
    sub = active_subscription(db, current_user.id)
    if not sub:
        raise HTTPException(status_code=400, detail="当前没有生效中的付费订阅")
    if sub.status == "cancelled":
        return {"status": "cancelled", "message": "订阅已取消，权益保留至到期"}
    sub.status = "cancelled"
    db.commit()
    logger.info("用户 %s 取消订阅 %s（%s），权益保留至 %s",
                current_user.id, sub.plan_code, sub.period, sub.end_at)
    return {"status": "cancelled", "message": "已取消订阅，本周期内可继续使用，到期后降级为免费版"}
