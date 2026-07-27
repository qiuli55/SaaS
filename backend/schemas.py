from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ========== 用户 ==========
class UserRegister(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11, pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=32)
    name: Optional[str] = ""
    firm_name: Optional[str] = ""


class UserLogin(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    password: str = Field(..., min_length=6, max_length=32)


class UserInfo(BaseModel):
    id: int
    phone: str
    name: str
    firm_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 案件 ==========
class CaseCreate(BaseModel):
    case_type: Optional[str] = ""
    plaintiff: Optional[str] = ""
    defendant: Optional[str] = ""
    subject_amount: Optional[float] = 0
    commission_date: Optional[date] = None
    description: Optional[str] = ""
    status: Optional[str] = "进行中"


class CaseUpdate(BaseModel):
    case_type: Optional[str] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    subject_amount: Optional[float] = None
    commission_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CaseInfo(BaseModel):
    id: int
    user_id: int
    case_no: str
    case_type: str
    plaintiff: str
    defendant: str
    subject_amount: float
    status: str
    commission_date: Optional[date]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    document_count: Optional[int] = 0
    file_count: Optional[int] = 0

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    total: int
    items: List[CaseInfo]
    page: int
    page_size: int


# ========== 文书 ==========
class DocumentGenerate(BaseModel):
    case_id: int
    doc_type: str
    claims: Optional[str] = ""
    facts: Optional[str] = ""


class DocumentInfo(BaseModel):
    id: int
    case_id: int
    doc_type: str
    version: int
    form_data: Optional[dict]
    final_content: Optional[str]
    verified_articles: Optional[list]
    status: str
    created_at: datetime
    case_name: Optional[str] = ""
    plaintiff: Optional[str] = ""
    defendant: Optional[str] = ""

    class Config:
        from_attributes = True


# ========== 文件 ==========
class FileInfo(BaseModel):
    id: int
    case_id: int
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 通用 ==========
class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
