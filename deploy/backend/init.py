import os, sys, sqlite3, random, bcrypt

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 1. 停掉可能的旧进程
os.system("taskkill /F /IM python.exe >nul 2>&1")

# 2. 删库 + 清缓存
for path in ["legal_ai.db", "uploads/legal_ai.db", "__pycache__"]:
    if os.path.exists(path):
        if os.path.isdir(path):
            for f in os.listdir(path):
                try: os.remove(os.path.join(path, f))
                except: pass
            try: os.rmdir(path)
            except: pass
        else:
            os.remove(path)

# 3. 强制 SQLAlchemy 建表（用最新模型）
from database import Base, engine, SessionLocal
from models import User
Base.metadata.create_all(bind=engine)

# 4. 校验 schema
conn = sqlite3.connect("legal_ai.db")
cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
print("users 表字段:", cols)
if "user_code" not in cols:
    print("ERROR: user_code 字段不存在！")
    sys.exit(1)
conn.close()

# 5. 插入测试账号
db = SessionLocal()
existing = db.query(User).filter(User.phone == "13800138000").first()
if existing:
    print("测试账号已存在，跳过")
else:
    code = str(random.randint(10000000, 99999999))
    pwd = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
    db.add(User(phone="13800138000", user_code=code, password_hash=pwd,
                name="管理员", firm_name="测试律所"))
    db.commit()
    print(f"✓ 测试账号创建: 13800138000 / 123456")
db.close()

print("\n启动后端命令: python -X utf8 -m uvicorn main:app --host 0.0.0.0 --port 8001")
