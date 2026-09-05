"""团队协作"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Team, TeamMember, User, Case
from auth import get_current_user

router = APIRouter(prefix="/api/teams", tags=["团队"])


class TeamCreate(BaseModel):
    name: str
    description: str = ""


class InviteReq(BaseModel):
    phone: str = ""  # 手机号或数字ID
    user_code: str = ""


def _require_member(team_id: int, user: User, db: Session) -> TeamMember:
    """调用者必须是该团队成员，否则 403"""
    tm = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user.id
    ).first()
    if not tm:
        raise HTTPException(status_code=403, detail="你不是该团队成员，无权操作")
    return tm


def _require_owner(team_id: int, user: User, db: Session) -> TeamMember:
    tm = _require_member(team_id, user, db)
    if tm.role != "owner":
        raise HTTPException(status_code=403, detail="只有团队所有者可执行此操作")
    return tm


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
    """列出我所在的所有团队（批量查询，避免 N+1）"""
    memberships = db.query(TeamMember).filter(TeamMember.user_id == user.id).all()
    if not memberships:
        return []

    team_ids = [m.team_id for m in memberships]
    my_roles = {m.team_id: m.role for m in memberships}

    # 一次取回团队、成员、成员用户、案件计数
    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    all_members = db.query(TeamMember).filter(TeamMember.team_id.in_(team_ids)).all()
    member_ids = {tm.user_id for tm in all_members}
    users = (
        {u.id: u for u in db.query(User).filter(User.id.in_(member_ids)).all()}
        if member_ids else {}
    )
    members_by_team = {}
    for tm in all_members:
        members_by_team.setdefault(tm.team_id, []).append(tm)
    case_counts = dict(
        db.query(Case.team_id, func.count(Case.id))
        .filter(Case.team_id.in_(team_ids))
        .group_by(Case.team_id)
        .all()
    )

    result = []
    for t in teams:
        member_users = []
        for tm in members_by_team.get(t.id, []):
            u = users.get(tm.user_id)
            if u:
                member_users.append({"id": u.id, "name": u.name or u.phone, "role": tm.role})
        result.append({
            "id": t.id, "name": t.name, "description": t.description,
            "owner_id": t.owner_id, "my_role": my_roles.get(t.id),
            "members": member_users, "case_count": case_counts.get(t.id, 0),
        })
    return result


@router.get("/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    _require_member(team_id, user, db)
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "团队不存在")

    members = db.query(TeamMember).filter(TeamMember.team_id == t.id).all()
    member_ids = [m.user_id for m in members]
    users = {u.id: u for u in db.query(User).filter(User.id.in_(member_ids)).all()} if member_ids else {}
    member_users = [
        {"id": u.id, "name": u.name or u.phone, "phone": u.phone, "role": m.role}
        for m in members if (u := users.get(m.user_id))
    ]
    cases = db.query(Case).filter(Case.team_id == t.id).all()
    return {
        "id": t.id, "name": t.name, "description": t.description,
        "owner_id": t.owner_id, "members": member_users,
        "cases": [{"id": c.id, "case_no": c.case_no, "case_type": c.case_type,
                    "plaintiff": c.plaintiff, "defendant": c.defendant, "status": c.status} for c in cases],
    }


@router.post("/{team_id}/invite")
def invite_member(team_id: int, req: InviteReq, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """邀请用户加入团队（仅所有者）"""
    _require_owner(team_id, user, db)
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "团队不存在")

    if req.user_code:
        invitee = db.query(User).filter(User.user_code == req.user_code).first()
    else:
        invitee = db.query(User).filter(User.phone == req.phone).first()

    if not invitee:
        raise HTTPException(404, "未找到该用户，请确认手机号或数字 ID 正确")
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == invitee.id).first()
    if existing:
        return {"message": "该用户已在团队中"}
    db.add(TeamMember(team_id=team_id, user_id=invitee.id, role="member"))
    db.commit()
    return {"message": f"已邀请 {invitee.name or invitee.phone} 加入团队"}


@router.delete("/{team_id}/members/{member_id}")
def remove_member(team_id: int, member_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """移除成员（仅所有者，或成员自己退出）"""
    _require_member(team_id, user, db)
    if user.id != member_id:
        _require_owner(team_id, user, db)
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
    """取消案件共享（仅案件所有者）"""
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == user.id, Case.team_id == team_id).first()
    if not case:
        raise HTTPException(404, "案件不存在或无权限")
    case.team_id = None
    db.commit()
    return {"message": "已取消共享"}


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """解散团队（仅 owner 可操作）"""
    _require_owner(team_id, user, db)
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "团队不存在")

    # 先解除所有关联案件
    db.query(Case).filter(Case.team_id == team_id).update({Case.team_id: None})
    # 删除所有成员
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    # 删除团队
    db.delete(t)
    db.commit()
    return {"message": "团队已解散"}
