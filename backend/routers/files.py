import os
import uuid
import shutil
import zipfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import io

from database import get_db
from models import CaseFile, Case, User
from schemas import FileInfo
from auth import get_current_user

router = APIRouter(tags=["文件"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB

# 确保上传目录存在
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

FILE_TYPE_MAP = {
    "证据": "evidence",
    "判决书": "judgment",
    "委托书": "entrustment",
    "其他": "other",
}


@router.post("/api/cases/{case_id}/files")
async def upload_files(
    case_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter(
        Case.id == case_id, Case.user_id == current_user.id
    ).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")

    uploaded = []
    for upload_file in files:
        # 检查文件大小
        content = await upload_file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"文件 {upload_file.filename} 超过大小限制（50MB）")
        await upload_file.seek(0)

        # 生成唯一文件名，防止覆盖
        ext = Path(upload_file.filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        relative_path = f"cases/{case_id}/{unique_name}"
        absolute_path = os.path.join(UPLOAD_DIR, relative_path)

        # 确保子目录存在
        Path(absolute_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with open(absolute_path, "wb") as f:
            f.write(content)

        # 推断文件类型
        file_type = "other"
        fname_lower = upload_file.filename.lower()
        if any(kw in fname_lower for kw in ["证据", "evidence", "proof"]):
            file_type = "evidence"
        elif any(kw in fname_lower for kw in ["判决", "judgment", "裁定", "ruling"]):
            file_type = "judgment"
        elif any(kw in fname_lower for kw in ["委托", "entrust", "授权", "authorization", "代理"]):
            file_type = "entrustment"

        case_file = CaseFile(
            case_id=case_id,
            user_id=current_user.id,
            file_name=upload_file.filename,
            file_type=file_type,
            file_size=len(content),
            file_path=relative_path,
            mime_type=upload_file.content_type or "application/octet-stream",
        )
        db.add(case_file)
        uploaded.append(case_file)

    db.commit()
    for f in uploaded:
        db.refresh(f)

    return {
        "code": 0,
        "message": "上传成功",
        "data": [FileInfo.model_validate(f).model_dump() for f in uploaded],
    }


@router.get("/api/cases/{case_id}/files")
def list_files(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter(
        Case.id == case_id, Case.user_id == current_user.id
    ).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")

    files = db.query(CaseFile).filter(
        CaseFile.case_id == case_id
    ).order_by(CaseFile.created_at.desc()).all()

    return {
        "code": 0,
        "data": [FileInfo.model_validate(f).model_dump() for f in files],
    }


@router.get("/api/files/{file_id}/preview")
def preview_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cf = db.query(CaseFile).filter(CaseFile.id == file_id).first()
    if not cf:
        raise HTTPException(status_code=404, detail="文件不存在")

    absolute_path = os.path.join(UPLOAD_DIR, cf.file_path)
    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail="文件已丢失")

    return FileResponse(absolute_path, media_type=cf.mime_type)


@router.get("/api/files/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cf = db.query(CaseFile).filter(CaseFile.id == file_id).first()
    if not cf:
        raise HTTPException(status_code=404, detail="文件不存在")

    absolute_path = os.path.join(UPLOAD_DIR, cf.file_path)
    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail="文件已丢失")

    return FileResponse(
        absolute_path,
        media_type=cf.mime_type,
        filename=cf.file_name,
    )


@router.get("/api/cases/{case_id}/files/download-all")
def download_all_files(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    files = db.query(CaseFile).filter(
        CaseFile.case_id == case_id, CaseFile.user_id == current_user.id
    ).all()

    if not files:
        raise HTTPException(status_code=404, detail="没有文件可下载")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for cf in files:
            absolute_path = os.path.join(UPLOAD_DIR, cf.file_path)
            if os.path.exists(absolute_path):
                zf.write(absolute_path, cf.file_name)

    buf.seek(0)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=case_{case_id}_files.zip"},
    )


@router.delete("/api/files/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cf = db.query(CaseFile).filter(CaseFile.id == file_id).first()
    if not cf:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 删除物理文件
    absolute_path = os.path.join(UPLOAD_DIR, cf.file_path)
    if os.path.exists(absolute_path):
        os.remove(absolute_path)

    db.delete(cf)
    db.commit()

    return {"code": 0, "message": "已删除"}
