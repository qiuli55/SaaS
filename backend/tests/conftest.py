"""测试基础设施：独立 SQLite DB + 测试客户端 + 认证 fixture"""
import os
import sys
import pytest
from pathlib import Path

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["TESTING"] = "1"

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test_legal_ai.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# 测试模式：跳过短信验证
import routers.user as _user_mod
_user_mod.verify_sms_code = lambda phone, code: True

from models import User, InviteCode


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    db_path = Path("test_legal_ai.db")
    if db_path.exists():
        db_path.unlink()
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_db():
    yield
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())

    # 每个测试后补一条邀请码
    db = TestSessionLocal()
    try:
        db.add(InviteCode(code="INVITE0001", created_by=0))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def api():
    return client


_counter = 1000  # 高位起始，避免与测试中硬编码的手机号冲突


def fresh_phone():
    global _counter
    _counter += 1
    return f"138{_counter:08d}"


def fresh_auth(api):
    phone = fresh_phone()
    code = f"INV{_counter:06d}"
    # 为本次注册预置唯一的邀请码
    db = TestSessionLocal()
    try:
        from sqlalchemy import text
        db.execute(text("INSERT OR IGNORE INTO invite_codes (code, created_by) VALUES (:c, 0)"), {"c": code})
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    r = api.post("/api/user/register", json={
        "phone": phone, "password": "Test1234", "name": "Test",
        "code": "123456", "invite_code": code, "firm_name": "TestFirm",
    })
    assert r.status_code == 200, f"register failed: {r.json()}"
    r2 = api.post("/api/user/login", json={"phone": phone, "password": "Test1234"})
    assert r2.status_code == 200, f"login failed: {r2.json()}"
    return {"Authorization": f"Bearer {r2.json()['access_token']}"}


@pytest.fixture
def auth(api):
    return fresh_auth(api)
