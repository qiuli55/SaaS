"""ORM 模型定义：用户/案件/客户/文书/日程/团队/订阅计费等全部表结构。"""
from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, Date, DateTime,
    Boolean, ForeignKey, JSON, func
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(11), unique=True, nullable=False, index=True)
    user_code = Column(String(8), unique=True, nullable=True)  # 8位唯一数字ID
    password_hash = Column(String(128), nullable=False)
    name = Column(String(50), default="")
    firm_name = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    cases = relationship("Case", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    case_no = Column(String(50), default="")
    case_type = Column(String(50), default="")
    plaintiff = Column(String(100), default="")
    defendant = Column(String(100), default="")
    plaintiff_detail = Column(Text, default="")  # JSON: {address, id_card, phone, gender, birth...}
    defendant_detail = Column(Text, default="")  # JSON: {address, legal_rep, id_card, phone...}
    court_name = Column(String(100), default="")  # 管辖法院
    subject_amount = Column(DECIMAL(12, 2), default=0)
    status = Column(String(20), default="进行中")
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    commission_date = Column(Date, nullable=True)
    description = Column(Text, default="")
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    notes = Column(Text, default="")  # AI 分析结果等附加备注
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="cases")
    client = relationship("Client", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    files = relationship("CaseFile", back_populates="case", cascade="all, delete-orphan")
    team = relationship("Team")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type = Column(String(20), default="起诉状")
    version = Column(Integer, default=1)
    form_data = Column(JSON, default=dict)
    ai_raw_text = Column(Text, default="")
    final_content = Column(Text, default="")
    verified_articles = Column(JSON, default=list)
    status = Column(String(20), default="草稿")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="documents")
    case = relationship("Case", back_populates="documents")


class CaseFile(Base):
    __tablename__ = "case_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(200), default="")
    file_type = Column(String(20), default="other")
    file_size = Column(Integer, default=0)
    file_path = Column(String(500), default="")
    mime_type = Column(String(50), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="files")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), default="")
    phone = Column(String(20), default="")
    wechat = Column(String(50), default="")
    id_card = Column(String(18), default="")
    company = Column(String(100), default="")
    tags = Column(Text, default="")  # JSON array string
    remark = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    cases = relationship("Case", back_populates="client")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(20), default="待办")  # 开庭/举证/立案/上诉截止/待办
    event_date = Column(DateTime, nullable=False)
    location = Column(String(200), default="")
    notes = Column(Text, default="")
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    case = relationship("Case")


class VisitLog(Base):
    """访问日志"""
    __tablename__ = "visit_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), index=True)
    path = Column(String(500))
    method = Column(String(10))
    created_at = Column(DateTime, default=func.now())


class Team(Base):
    """协作团队"""
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(500))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User")


class TeamMember(Base):
    """团队成员"""
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(20), default="member")
    joined_at = Column(DateTime, default=func.now())

    team = relationship("Team")
    user = relationship("User")


class CaseDeadline(Base):
    """案件审限/截止日期"""
    __tablename__ = "case_deadlines"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    deadline_type = Column(String(30))   # 答辩期/举证期限/上诉期/开庭/管辖权异议/自定义
    deadline_date = Column(DateTime)
    notes = Column(String(200))
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    case = relationship("Case")
    user = relationship("User")


class LawFirm(Base):
    """律师事务所名录"""
    __tablename__ = "law_firms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True)
    city = Column(String(50))
    created_at = Column(DateTime, default=func.now())


class InviteCode(Base):
    """邀请码"""
    __tablename__ = "invite_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(12), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime, nullable=True)

    creator = relationship("User", foreign_keys=[created_by])
    user = relationship("User", foreign_keys=[used_by])


class UsageLog(Base):
    """AI用量日志"""
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_type = Column(String(20), nullable=False)  # chat/contract/case_analysis/document
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")


class Plan(Base):
    """订阅套餐定义"""
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # free/basic/pro
    name = Column(String(50), nullable=False)
    price_monthly = Column(DECIMAL(10, 2), default=0)
    price_yearly = Column(DECIMAL(10, 2), default=0)
    daily_limit = Column(Integer, nullable=True)  # None = 不限量
    features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """用户订阅记录（仅保留当前/历史，active 为生效中）"""
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    plan_code = Column(String(20), nullable=False)  # 冗余，便于展示
    status = Column(String(20), default="active")  # active/cancelled/expired
    period = Column(String(10), default="monthly")  # monthly/yearly
    start_at = Column(DateTime, default=func.now())
    end_at = Column(DateTime, nullable=True)  # 过期时间；active 且 end_at 已过则视为失效
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    plan = relationship("Plan", back_populates="subscriptions")


class Order(Base):
    """购买订单（当前为模拟支付，预留真实支付字段）"""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    plan_code = Column(String(20), nullable=False)
    plan_name = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), default=0)
    period = Column(String(10), default="monthly")  # monthly/yearly
    status = Column(String(20), default="pending")  # pending/paid/cancelled
    pay_method = Column(String(20), default="mock")  # mock/wxpay/alipay（预留）
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    plan = relationship("Plan")
