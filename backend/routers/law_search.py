"""《民法典》法条检索（两段式：先文件检索，再 AI 检索）

流程：
1. 文件检索：用户提问 → 在 minfadian.json（1260 条民法典）中按中文 n-gram 重叠打分，取相关法条 top-N
2. AI 检索：把命中的法条作为上下文，调用 DeepSeek 生成「基于法条」的回答

词条库缺失时整体优雅降级。
"""
import re
import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import User
# 复用 citation.load_law_db：依赖其"库缺失返回 None"的降级约定
from .citation import load_law_db
# 复用 contract._ask_deepseek：依赖其"未配 Key 时返回提示文案而不抛错"的约定
from .contract import _ask_deepseek, CONTRACT_API_KEY
from .quota import check_quota

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/law", tags=["法条检索"])

_HAN = re.compile(r"[\u4e00-\u9fff]")


def _ngrams(s: str, n: int):
    """生成字符串里的连续中文 n-gram 集合。"""
    return {s[i:i + n] for i in range(len(s) - n + 1)
            if _HAN.match(s[i]) and _HAN.match(s[i + n - 1])}


@lru_cache(maxsize=1)
def _load_indexed():
    """加载法条库并预构建每条法条的 n-gram 索引（缓存）。"""
    db = load_law_db()
    if not db:
        return None
    items = []
    for num, art in db["law"].items():
        text = art.get("text", "")
        grams = set()
        for n in (2, 3):
            if len(text) >= n:
                grams |= _ngrams(text, n)
        items.append((num, art, grams))
    return items


def retrieve(query: str, top: int = 8):
    """第一步：从法条文件检索与 query 最相关的法条（中文 n-gram 重叠打分）。"""
    items = _load_indexed()
    if not items:
        return []
    q = re.sub(r"[^\u4e00-\u9fff]", "", query)
    if len(q) < 2:
        return []
    qgrams = set()
    for n in (2, 3):
        if len(q) >= n:
            qgrams |= _ngrams(q, n)
    if not qgrams:
        return []
    scored = []
    for num, art, grams in items:
        hit = len(qgrams & grams)  # 命中的 n-gram 数
        if hit:
            scored.append((hit, num, art))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "id": num,
            "article": art.get("article", ""),
            "zhang": art.get("zhang", ""),
            "text": art.get("text", ""),
        }
        for _, num, art in scored[:top]
    ]


async def ai_search(query: str, retrieved):
    """第二步：把命中法条作为上下文，调用 AI 生成基于法条的回答。"""
    if not retrieved:
        return "未在《民法典》法条库中检索到与问题相关的条款。建议补充更具体的法律事实（如合同类型、争议焦点），或咨询执业律师。"
    context = "\n".join(
        f"第{r['id']}条（{r['zhang']}）：{r['text']}" for r in retrieved
    )
    system = (
        "你是精通《中华人民共和国民法典》的法律AI助手。"
        "请仅依据下方提供的法条回答用户问题，回答时明确引用条号（如「民法典第X条」）。"
        "如提供的法条不足以完整回答，请如实说明，不要编造条号或法条内容。"
    )
    user = f"【用户问题】\n{query}\n\n【检索到的《民法典》法条】\n{context}"
    return await _ask_deepseek(system, user, api_key=CONTRACT_API_KEY)


class LawSearchReq(BaseModel):
    query: str
    limit: int = 8


@router.post("/search", summary="法条两段式检索：先文件检索再 AI 检索")
async def law_search(
    req: LawSearchReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """法条检索接口：先本地法条库召回 top-N，再把命中法条交给 AI 生成带条号的回答。"""
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query 不能为空")
    if not check_quota(user.id, "law_search", db):
        logger.info("用户 %s 法条检索配额已用完", user.id)
        raise HTTPException(status_code=429, detail="今日 AI 调用次数已用完，请明日再试或升级套餐")
    retrieved = retrieve(req.query.strip(), max(1, min(req.limit, 20)))
    answer = await ai_search(req.query.strip(), retrieved)
    logger.info("法条检索 user=%s query=%r 命中=%s 条", user.id, req.query[:30], len(retrieved))
    return {
        "query": req.query.strip(),
        "retrieved_count": len(retrieved),
        "retrieved": retrieved,
        "answer": answer,
    }
