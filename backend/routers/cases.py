from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database import get_db
from models import Case, Document, CaseFile, User
from schemas import CaseCreate, CaseUpdate, CaseInfo, CaseListResponse
from auth import get_current_user

router = APIRouter(prefix="/api/cases", tags=["案件"])


def make_case_info(case: Case) -> CaseInfo:
    return CaseInfo(
        id=case.id,
        user_id=case.user_id,
        case_no=case.case_no,
        case_type=case.case_type,
        plaintiff=case.plaintiff,
        defendant=case.defendant,
        subject_amount=float(case.subject_amount or 0),
        status=case.status,
        commission_date=case.commission_date,
        description=case.description,
        created_at=case.created_at,
        updated_at=case.updated_at,
        document_count=len(case.documents) if case.documents else 0,
        file_count=len(case.files) if case.files else 0,
    )


@router.get("")
def list_cases(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="案件状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Case).filter(Case.user_id == current_user.id)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (Case.case_type.contains(kw)) |
            (Case.plaintiff.contains(kw)) |
            (Case.defendant.contains(kw)) |
            (Case.case_no.contains(kw))
        )
    if status:
        query = query.filter(Case.status == status)

    total = query.count()
    cases = query.order_by(Case.updated_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return CaseListResponse(
        total=total,
        items=[make_case_info(c) for c in cases],
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CaseInfo)
def create_case(
    req: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Generate case_no
    count_today = db.query(Case).filter(
        Case.user_id == current_user.id
    ).count() + 1
    case_no = f"LA-{current_user.id:04d}-{count_today:04d}"

    case = Case(
        user_id=current_user.id,
        case_no=case_no,
        case_type=req.case_type,
        plaintiff=req.plaintiff,
        defendant=req.defendant,
        subject_amount=req.subject_amount or 0,
        commission_date=req.commission_date,
        description=req.description,
        status=req.status or "进行中",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return make_case_info(case)


@router.get("/{case_id}", response_model=CaseInfo)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter(
        Case.id == case_id, Case.user_id == current_user.id
    ).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    return make_case_info(case)


@router.put("/{case_id}", response_model=CaseInfo)
def update_case(
    case_id: int,
    req: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter(
        Case.id == case_id, Case.user_id == current_user.id
    ).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")

    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(case, k, v)

    db.commit()
    db.refresh(case)
    return make_case_info(case)


@router.delete("/{case_id}")
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter(
        Case.id == case_id, Case.user_id == current_user.id
    ).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")
    db.delete(case)
    db.commit()
    return {"code": 0, "message": "已删除"}
