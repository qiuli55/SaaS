"""生成 Lexi 莱希 内测邀请码（直接操作数据库，不需要后端在跑）

用法：
    python scripts/gen_invites.py            # 默认生成 20 个
    python scripts/gen_invites.py 50         # 生成 50 个
    python scripts/gen_invites.py 20 --csv   # 同时导出 CSV
"""
import sys
import csv
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path

# 让脚本能 import backend 顶层模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import SessionLocal  # noqa: E402
from models import User, InviteCode  # noqa: E402


def main(count: int = 20, export_csv: bool = False) -> None:
    if count < 1 or count > 1000:
        print("数量应在 1~1000 之间")
        return

    chars = string.ascii_uppercase + string.digits
    db = SessionLocal()
    try:
        creator = db.query(User).first()
        if not creator:
            print("❌ 数据库里还没用户，先注册一个账号")
            return

        created: list[str] = []
        skipped = 0
        for _ in range(count):
            code = None
            for _ in range(10):
                candidate = "".join(secrets.choice(chars) for _ in range(12))
                if not db.query(InviteCode).filter(InviteCode.code == candidate).first():
                    code = candidate
                    break
            if not code:
                skipped += 1
                continue
            db.add(InviteCode(
                code=code,
                created_by=creator.id,
                created_at=datetime.now(timezone.utc),
            ))
            created.append(code)
        db.commit()

        # 输出
        print(f"\n=== 新增 {len(created)} 个邀请码（创建者：user#{creator.id} {creator.phone}）===\n")
        for i, c in enumerate(created, 1):
            print(f"  {i:>2}. {c}")

        print("\n--- 一行粘贴版（用于发小红书 / 私信）---")
        print(" ".join(created))

        if skipped:
            print(f"\n（{skipped} 个因冲突跳过，可重跑）")

        if export_csv and created:
            out = Path(__file__).parent.parent / f"invite_codes_{datetime.now():%Y%m%d_%H%M%S}.csv"
            with out.open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["序号", "邀请码"])
                for i, c in enumerate(created, 1):
                    w.writerow([i, c])
            print(f"\n--- CSV 已导出 ---\n{out}")

    finally:
        db.close()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20
    csv_flag = "--csv" in sys.argv
    main(count=n, export_csv=csv_flag)
