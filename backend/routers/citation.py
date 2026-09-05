"""《民法典》法条引用校验（确定性底座）

把 skill 文件夹里的 validate_citations.py 逻辑移植为后端模块：
- 加载 backend/data/minfadian.json（1260 条民法典权威条文）
- 从文本中抽取《民法典》第X条引用，逐条核对条号是否真实存在
- 抓"虚构条号 / 笔误"，为合同审查报告提供可核验的法条依据

词条库缺失时整体优雅降级，不影响主流程。
"""
import json
import re
import logging
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/citation", tags=["法条校验"])

# 法条库路径：backend/data/minfadian.json
_DB_PATH = Path(__file__).parent.parent / "data" / "minfadian.json"

# 中文数字 -> int
_DIGITS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
           "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_UNITS = {"十": 10, "百": 100, "千": 1000}


def _cn2int(s: str) -> int:
    """中文数字转 int："二百三十"→230，"十"→10，纯阿拉伯数字直接转换。"""
    s = s.strip()
    if s.isdigit():
        return int(s)
    section = number = 0
    for ch in s:
        if ch in _DIGITS:
            number = _DIGITS[ch]
        elif ch in _UNITS:
            number = number or 1
            section += number * _UNITS[ch]
            number = 0
    return section + number


# 仅匹配带《民法典》/民法典 前缀的引用，避免把"合同第X条"误判为法条
_RE_CITE = re.compile(r"(?:《民法典》|民法典)\s*第\s*([零一二三四五六七八九十百千两0-9]+)\s*条")


@lru_cache(maxsize=1)
def load_law_db():
    """加载法条库（进程内只加载一次），失败返回 None（优雅降级）。"""
    if not _DB_PATH.exists():
        logger.warning("民法典法条库缺失: %s，法条校验将跳过", _DB_PATH)
        return None
    try:
        with open(_DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        law = {a["id"]: a for a in db.get("articles", [])}
        logger.info("民法典法条库加载完成，共 %s 条", len(law))
        return {"law": law, "count": db.get("count", len(law))}
    except Exception as e:
        logger.warning("民法典法条库加载失败: %s", e)
        return None


def check_citations(text: str):
    """抽取文本中《民法典》引用并逐条核验。返回 (条目列表, 库是否可用)。"""
    db = load_law_db()
    matches = list(_RE_CITE.finditer(text or ""))
    if not db:
        return None, False  # 库不可用
    results = []
    for m in matches:
        num = _cn2int(m.group(1))
        art = db["law"].get(num)
        if art is None:
            results.append({
                "id": num,
                "status": "NOT_FOUND",
                "message": f"民法典中不存在第{num}条，疑似虚构条号或笔误，请复核",
            })
        else:
            results.append({
                "id": num,
                "status": "FOUND",
                "article": art["article"],
                "zhang": art.get("zhang", ""),
                "text": art.get("text", ""),
            })
    return results, True


def render_citation_section(text: str) -> str:
    """生成"法条引用核验"段（Markdown）。库不可用时返回空串（不污染报告）。"""
    results, ok = check_citations(text)
    if not ok or results is None:
        return ""
    found = [r for r in results if r["status"] == "FOUND"]
    not_found = [r for r in results if r["status"] == "NOT_FOUND"]
    lines = [
        "## 七、法条引用核验",
        "",
        "> 本段由系统自动比对《民法典》权威条文库（共 1260 条）生成，非 AI 生成，用于核验前文本报告所引条号是否真实存在。",
        "",
    ]
    if not results:
        lines.append("本报告未引用具体《民法典》条号，无需核验。")
        return "\n".join(lines)
    # 去重：同一条号+同状态只列一次（AI 可能在多处引用同一虚构条号）
    seen, unique = set(), []
    for r in results:
        key = (r["id"], r["status"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    lines.append(f"本报告引用《民法典》条款共 **{len(results)}** 处（去重后 **{len(unique)}** 条），核验结果如下：")
    lines.append("")
    for r in unique:
        if r["status"] == "FOUND":
            lines.append(f"- ✅ 第{r['id']}条（{r.get('zhang','')}）：命中，原文要点——{r['text'][:40]}{'…' if len(r['text'])>40 else ''}")
        else:
            lines.append(f"- ❌ 第{r['id']}条：{r['message']}")
    lines.append("")
    if not_found:
        lines.append(f"⚠️ 发现 **{len([r for r in unique if r['status']=='NOT_FOUND'])}** 条引用在《民法典》中不存在，可能为 AI 虚构条号或笔误，请人工复核对应风险点。")
    else:
        lines.append("✅ 本报告引用的《民法典》条款均已通过权威库核验，条号真实存在。")
    return "\n".join(lines)


class CitationCheckReq(BaseModel):
    text: str


@router.post("/validate")
async def validate_citations(req: CitationCheckReq,
                             user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """独立校验接口：传入任意文本，返回其中《民法典》引用的核验结果。"""
    results, ok = check_citations(req.text)
    if not ok:
        return {"available": False, "message": "民法典法条库未加载，校验不可用", "results": []}
    return {"available": True, "count": len(results), "results": results}
