from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Schedule, User, Case
from schemas import ScheduleCreate, ScheduleUpdate
from auth import get_current_user

router = APIRouter(prefix="/api/schedules", tags=["日程"])

VALID_EVENT_TYPES = ["开庭", "举证", "立案", "上诉截止", "待办"]


def make_schedule_info(s: Schedule) -> dict:
    case_name = None
    if s.case_id and s.case_id > 0:
        case = s.case  # 通过 relationship 获取
        if case:
            case_name = f"{case.plaintiff}{case.case_type}"
    return {
        "id": s.id,
        "case_id": s.case_id if s.case_id and s.case_id > 0 else None,
        "event_type": s.event_type,
        "event_date": s.event_date.isoformat() if s.event_date else "",
        "location": s.location,
        "notes": s.notes,
        "is_done": s.is_done,
        "case_name": case_name,
    }


@router.get("")
def list_schedules(
    month: str = Query(None, description="YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Schedule).filter(Schedule.user_id == current_user.id)
    if month:
        try:
            year, m = int(month[:4]), int(month[5:7])
            from datetime import date
            start = date(year, m, 1)
            if m == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, m + 1, 1)
            query = query.filter(Schedule.event_date >= start, Schedule.event_date < end)
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="月份格式错误，请使用 YYYY-MM 格式")

    schedules = query.order_by(Schedule.event_date.asc()).all()
    return {"code": 0, "data": [make_schedule_info(s) for s in schedules]}


@router.post("")
def create_schedule(
    data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.event_type not in VALID_EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的日程类型，可选：{', '.join(VALID_EVENT_TYPES)}")

    case_id = data.case_id if data.case_id and data.case_id > 0 else None
    # 如果指定了 case_id，验证案件归属
    if case_id:
        case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()
        if not case:
            raise HTTPException(status_code=404, detail="关联案件不存在")

    s = Schedule(
        case_id=case_id,
        user_id=current_user.id,
        event_type=data.event_type,
        event_date=data.event_date,
        location=data.location or "",
        notes=data.notes or "",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"code": 0, "message": "已添加", "data": make_schedule_info(s)}


@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="日程不存在")

    update_data = data.model_dump(exclude_unset=True)
    if "event_type" in update_data and update_data["event_type"] not in VALID_EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的日程类型，可选：{', '.join(VALID_EVENT_TYPES)}")

    for k, v in update_data.items():
        setattr(s, k, v)

    db.commit()
    return {"code": 0, "message": "已更新", "data": make_schedule_info(s)}


@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="日程不存在")
    db.delete(s)
    db.commit()
    return {"code": 0, "message": "已删除"}
