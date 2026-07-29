"""邀请码管理"""
import secrets, string
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, InviteCode
from auth import get_current_user
from schemas import InviteCodeBatch, InviteCodeInfo

router = APIRouter(prefix="/api/invite", tags=["邀请码"])


def _gen_code() -> str:
    """生成12位邀请码（字母数字混合）"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(12))


@router.post("/generate", response_model=list[InviteCodeInfo])
def generate_codes(
    batch: InviteCodeBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量生成邀请码"""
    codes = []
    for _ in range(batch.count):
        for attempt in range(10):
            code = _gen_code()
            if not db.query(InviteCode).filter(InviteCode.code == code).first():
                break
        ic = InviteCode(code=code, created_by=current_user.id)
        db.add(ic)
        db.flush()
        codes.append(InviteCodeInfo(
            id=ic.id, code=ic.code,
            is_used=False,
            created_at=ic.created_at,
        ))
    db.commit()
    return codes


@router.get("/list", response_model=list[InviteCodeInfo])
def list_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看所有邀请码"""
    rows = db.query(InviteCode).order_by(InviteCode.created_at.desc()).all()
    result = []
    for r in rows:
        phone = None
        if r.used_by:
            u = db.query(User).filter(User.id == r.used_by).first()
            phone = u.phone if u else None
        result.append(InviteCodeInfo(
            id=r.id, code=r.code,
            is_used=r.is_used,
            created_at=r.created_at,
            used_at=r.used_at,
            used_by=r.used_by,
            used_by_phone=phone,
        ))
    return result


@router.post("/validate")
def validate_code(code: str, db: Session = Depends(get_db)):
    """校验邀请码是否可用"""
    ic = db.query(InviteCode).filter(InviteCode.code == code.strip().upper()).first()
    if not ic:
        raise HTTPException(400, "邀请码无效")
    if ic.is_used:
        raise HTTPException(400, "邀请码已被使用")
    return {"valid": True, "code": ic.code}
