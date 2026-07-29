"""团队协作"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Team, TeamMember, User, Case
from auth import get_current_user

router = APIRouter(prefix="/api/teams", tags=["团队"])


class TeamCreate(BaseModel):
    name: str
    description: str = ""


class InviteReq(BaseModel):
    phone: str  # 被邀请人手机号


@router.post("")
def create_team(req: TeamCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = Team(name=req.name, description=req.description, owner_id=user.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    # 创建者自动成为 owner 成员
    db.add(TeamMember(team_id=t.id, user_id=user.id, role="owner"))
    db.commit()
    return {"id": t.id, "name": t.name, "description": t.description}


@router.get("")
def list_teams(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """列出我所在的所有团队"""
    memberships = db.query(TeamMember).filter(TeamMember.user_id == user.id).all()
    teams = []
    for m in memberships:
        t = db.query(Team).filter(Team.id == m.team_id).first()
        if t:
            members = db.query(TeamMember).filter(TeamMember.team_id == t.id).all()
            member_users = []
            for tm in members:
                u = db.query(User).filter(User.id == tm.user_id).first()
                member_users.append({"id": u.id, "name": u.name or u.phone, "role": tm.role})
            team_cases = db.query(Case).filter(Case.team_id == t.id).count()
            teams.append({
                "id": t.id, "name": t.name, "description": t.description,
                "owner_id": t.owner_id, "my_role": m.role,
                "members": member_users, "case_count": team_cases,
            })
    return teams


@router.get("/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "团队不存在")
    members = db.query(TeamMember).filter(TeamMember.team_id == t.id).all()
    member_users = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        member_users.append({"id": u.id, "name": u.name or u.phone, "phone": u.phone, "role": m.role})
    cases = db.query(Case).filter(Case.team_id == t.id).all()
    return {
        "id": t.id, "name": t.name, "description": t.description,
        "owner_id": t.owner_id, "members": member_users,
        "cases": [{"id": c.id, "case_no": c.case_no, "case_type": c.case_type,
                    "plaintiff": c.plaintiff, "defendant": c.defendant, "status": c.status} for c in cases],
    }


@router.post("/{team_id}/invite")
def invite_member(team_id: int, req: InviteReq, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """邀请用户加入团队"""
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "团队不存在")
    invitee = db.query(User).filter(User.phone == req.phone).first()
    if not invitee:
        raise HTTPException(404, "该手机号未注册，请先邀请对方注册")
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == invitee.id).first()
    if existing:
        return {"message": "该用户已在团队中"}
    db.add(TeamMember(team_id=team_id, user_id=invitee.id, role="member"))
    db.commit()
    return {"message": f"已邀请 {invitee.name or invitee.phone} 加入团队"}


@router.delete("/{team_id}/members/{member_id}")
def remove_member(team_id: int, member_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tm = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == member_id).first()
    if not tm:
        raise HTTPException(404, "成员不存在")
    db.delete(tm)
    db.commit()
    return {"message": "已移除"}


@router.put("/{team_id}/cases/{case_id}")
def share_case_to_team(team_id: int, case_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """将案件分配到团队"""
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == user.id).first()
    if not case:
        raise HTTPException(404, "案件不存在或无权限")
    case.team_id = team_id
    db.commit()
    return {"message": "已共享到团队"}


@router.delete("/{team_id}/cases/{case_id}")
def unshare_case(team_id: int, case_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    case = db.query(Case).filter(Case.id == case_id, Case.team_id == team_id).first()
    if not case:
        raise HTTPException(404, "案件不存在")
    case.team_id = None
    db.commit()
    return {"message": "已取消共享"}


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """解散团队（仅 owner 可操作）"""
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "团队不存在")
    if t.owner_id != user.id:
        raise HTTPException(403, "只有创建者可以解散团队")

    # 先解除所有关联案件
    db.query(Case).filter(Case.team_id == team_id).update({Case.team_id: None})
    # 删除所有成员
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    # 删除团队
    db.delete(t)
    db.commit()
    return {"message": "团队已解散"}
