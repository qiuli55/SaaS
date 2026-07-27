from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserInfo, TokenResponse
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.post("/register", response_model=TokenResponse)
def register(req: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    user = User(
        phone=req.phone,
        password_hash=hash_password(req.password),
        name=req.name or "",
        firm_name=req.firm_name or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserInfo.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserInfo.model_validate(user),
    )


@router.get("/info", response_model=UserInfo)
def get_info(current_user: User = Depends(get_current_user)):
    return UserInfo.model_validate(current_user)
