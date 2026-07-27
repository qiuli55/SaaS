from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Client, User, Case
from schemas import ClientCreate, ClientUpdate, ClientInfo
from auth import get_current_user

router = APIRouter(prefix="/api/clients", tags=["客户"])


@router.get("")
def list_clients(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Client).filter(Client.user_id == current_user.id)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (Client.name.contains(kw)) |
            (Client.phone.contains(kw)) |
            (Client.company.contains(kw))
        )

    total = query.count()
    clients = query.order_by(Client.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for c in clients:
        case_count = db.query(Case).filter(Case.client_id == c.id).count()
        items.append({
            "id": c.id,
            "user_id": c.user_id,
            "name": c.name,
            "phone": c.phone,
            "wechat": c.wechat,
            "id_card": c.id_card,
            "company": c.company,
            "tags": c.tags,
            "remark": c.remark,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "case_count": case_count,
        })

    return {"code": 0, "data": {"total": total, "items": items, "page": page, "page_size": page_size}}


@router.post("")
def create_client(
    req: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = Client(
        user_id=current_user.id,
        name=req.name or "",
        phone=req.phone or "",
        wechat=req.wechat or "",
        id_card=req.id_card or "",
        company=req.company or "",
        tags=req.tags or "",
        remark=req.remark or "",
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    return {
        "code": 0,
        "message": "创建成功",
        "data": {
            "id": client.id,
            "user_id": client.user_id,
            "name": client.name,
            "phone": client.phone,
            "wechat": client.wechat,
            "id_card": client.id_card,
            "company": client.company,
            "tags": client.tags,
            "remark": client.remark,
            "created_at": client.created_at.isoformat() if client.created_at else "",
            "case_count": 0,
        },
    }


@router.get("/{client_id}")
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(
        Client.id == client_id, Client.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户不存在")

    # 获取关联案件
    cases = db.query(Case).filter(Case.client_id == client_id).all()
    case_list = []
    for c in cases:
        case_list.append({
            "id": c.id,
            "case_no": c.case_no,
            "case_type": c.case_type,
            "plaintiff": c.plaintiff,
            "defendant": c.defendant,
            "status": c.status,
            "subject_amount": float(c.subject_amount or 0),
        })

    return {
        "code": 0,
        "data": {
            "id": client.id,
            "user_id": client.user_id,
            "name": client.name,
            "phone": client.phone,
            "wechat": client.wechat,
            "id_card": client.id_card,
            "company": client.company,
            "tags": client.tags,
            "remark": client.remark,
            "created_at": client.created_at.isoformat() if client.created_at else "",
            "case_count": len(case_list),
            "cases": case_list,
        },
    }


@router.put("/{client_id}")
def update_client(
    client_id: int,
    req: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(
        Client.id == client_id, Client.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户不存在")

    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(client, k, v)

    db.commit()
    db.refresh(client)

    return {
        "code": 0,
        "message": "更新成功",
        "data": {
            "id": client.id,
            "name": client.name,
            "phone": client.phone,
            "wechat": client.wechat,
            "id_card": client.id_card,
            "company": client.company,
            "tags": client.tags,
            "remark": client.remark,
        },
    }


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(
        Client.id == client_id, Client.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户不存在")
    db.delete(client)
    db.commit()
    return {"code": 0, "message": "已删除"}
