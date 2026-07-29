"""律所名录搜索"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import LawFirm

router = APIRouter(prefix="/api/firms", tags=["律所搜索"])


@router.get("/search")
def search_firms(q: str = Query(""), limit: int = Query(10), db: Session = Depends(get_db)):
    """模糊搜索律所"""
    if not q.strip():
        return []
    firms = db.query(LawFirm).filter(
        LawFirm.name.contains(q.strip())
    ).limit(limit).all()
    return [{"id": f.id, "name": f.name, "city": f.city or ""} for f in firms]
