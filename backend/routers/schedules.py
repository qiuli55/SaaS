from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Schedule, User
from auth import get_current_user

router = APIRouter(prefix="/api/schedules", tags=["日程"])


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
        except:
            pass

    schedules = query.order_by(Schedule.event_date.asc()).all()
    items = []
    for s in schedules:
        items.append({
            "id": s.id,
            "case_id": s.case_id,
            "event_type": s.event_type,
            "event_date": s.event_date.isoformat() if s.event_date else "",
            "location": s.location,
            "notes": s.notes,
            "is_done": s.is_done,
        })
    return {"code": 0, "data": items}


@router.post("")
def create_schedule(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        event_date = datetime.fromisoformat(data["event_date"])
    except:
        raise HTTPException(status_code=400, detail="日期格式错误")

    s = Schedule(
        case_id=data.get("case_id", 0),
        user_id=current_user.id,
        event_type=data.get("event_type", "待办"),
        event_date=event_date,
        location=data.get("location", ""),
        notes=data.get("notes", ""),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"code": 0, "message": "已添加", "data": {"id": s.id}}


@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="日程不存在")
    if "event_type" in data: s.event_type = data["event_type"]
    if "event_date" in data: s.event_date = datetime.fromisoformat(data["event_date"])
    if "location" in data: s.location = data["location"]
    if "notes" in data: s.notes = data["notes"]
    if "is_done" in data: s.is_done = data["is_done"]
    db.commit()
    return {"code": 0, "message": "已更新"}


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
