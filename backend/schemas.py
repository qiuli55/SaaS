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
    client_id: Optional[int] = None
    plaintiff_detail: Optional[str] = ""
    defendant_detail: Optional[str] = ""
    court_name: Optional[str] = ""


class CaseUpdate(BaseModel):
    case_type: Optional[str] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    subject_amount: Optional[float] = None
    commission_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None
    client_id: Optional[int] = None
    plaintiff_detail: Optional[str] = None
    defendant_detail: Optional[str] = None
    court_name: Optional[str] = None


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
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    plaintiff_detail: Optional[str] = ""
    defendant_detail: Optional[str] = ""
    court_name: Optional[str] = ""

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
    # 当事人详细信息
    plaintiff_info: Optional[str] = ""   # JSON: {name, gender, birth, id_card, address, phone}
    defendant_info: Optional[str] = ""   # JSON: {name, legal_rep, id_card, address, phone}
    court_name: Optional[str] = ""       # 管辖法院


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


# ========== 客户 (V2) ==========
class ClientCreate(BaseModel):
    name: Optional[str] = ""
    phone: Optional[str] = ""
    wechat: Optional[str] = ""
    id_card: Optional[str] = ""
    company: Optional[str] = ""
    tags: Optional[str] = ""
    remark: Optional[str] = ""


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    id_card: Optional[str] = None
    company: Optional[str] = None
    tags: Optional[str] = None
    remark: Optional[str] = None


class ClientInfo(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    wechat: str
    id_card: str
    company: str
    tags: str
    remark: str
    created_at: datetime
    case_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
