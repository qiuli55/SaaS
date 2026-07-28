from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import os
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserInfo, TokenResponse, UserUpdate, PasswordChange
from auth import hash_password, verify_password, create_access_token, get_current_user
from limiter import limiter

router = APIRouter(prefix="/api/user", tags=["用户"])

_TESTING = os.environ.get("TESTING") == "1"


def _account_key(request: Request) -> str:
    if _TESTING:
        import uuid
        return f"test:account:{uuid.uuid4().hex[:8]}"
    try:
        import json
        body_bytes = getattr(request, "_body", None)
        if not body_bytes:
            return f"account:nobody:{request.client.host or '?'}"
        data = json.loads(body_bytes)
        phone = data.get("phone") or data.get("account")
        return f"account:{phone}" if phone else f"account:nophone:{request.client.host or '?'}"
    except Exception:
        return f"account:err:{request.client.host or '?'}"


# ---- 装饰器（测试模式跳过）----
if _TESTING:
    register_deco = lambda f: f
    login_deco = lambda f: f
else:
    def register_deco(f):
        return limiter.limit("5/minute")(f)

    def login_deco(f):
        f1 = limiter.limit("10/minute")(f)
        f2 = limiter.limit("5/minute", key_func=_account_key)(f1)
        return f2


@router.post("/register", response_model=TokenResponse)
@register_deco
def register(req: UserRegister, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    user = User(
        phone=req.phone, password_hash=hash_password(req.password),
        name=req.name or "", firm_name=req.firm_name or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserInfo.model_validate(user))


@router.post("/login", response_model=TokenResponse)
@login_deco
def login(req: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserInfo.model_validate(user))


@router.get("/info", response_model=UserInfo)
def get_info(current_user: User = Depends(get_current_user)):
    return UserInfo.model_validate(current_user)


@router.put("/profile", response_model=UserInfo)
def update_profile(req: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(current_user, k, v)
    db.commit()
    db.refresh(current_user)
    return UserInfo.model_validate(current_user)


@router.put("/password")
def change_password(req: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if req.old_password == req.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与原密码相同")
    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"code": 0, "message": "密码修改成功"}
