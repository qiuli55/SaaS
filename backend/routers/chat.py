"""AI 法律对话助手"""
import os
import logging

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from .quota import check_quota
# 复用 anysearch.search：依赖其"未配 Key 或失败时返回空串"的约定
from .anysearch import search as web_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
ANYSEARCH_API_KEY = os.environ.get("ANYSEARCH_API_KEY", "")

SYSTEM_PROMPT = """你是一位资深中国执业律师，精通民法、刑法、行政法、诉讼法等法律领域。
你的职责是为律师同行提供专业的法律咨询服务，包括但不限于：
- 法律问题分析和解答
- 诉讼策略建议
- 法律文书写作指导
- 法条解释和案例参考

回答要求：
1. 引用中国现行法律法规，注明具体法条编号
2. 如涉及实务操作，给出可执行的建议步骤
3. 如问题超出你的知识范围或需要具体案件材料，诚实说明
4. 使用专业但易懂的中文，避免过多英文术语
5. 回答末尾如有需要，列出「建议进一步了解」的方向

注意：你不提供正式法律意见，仅供参考。"""


def is_legal_question(text: str) -> bool:
    """判断是否是需要检索的法律问题"""
    keywords = ["法条", "法规", "最新", "民法典", "刑法", "诉讼法", "司法解释",
                "2024", "2025", "2026", "修订", "施行", "生效", "废止",
                "怎么判", "案例", "判决", "裁定", "最高人民法院", "指导意见"]
    return any(kw in text for kw in keywords) or len(text) > 20


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # [{role: "user"/"assistant", content: "..."}]


async def _deepseek_chat(messages: list) -> tuple[bool, str]:
    """调用 DeepSeek 对话接口，返回 (是否成功, 回复文本或错误文案)。"""
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                DEEPSEEK_URL,
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": messages, "temperature": 0.5, "max_tokens": 2048},
            )
    except httpx.TimeoutException:
        logger.warning("DeepSeek 对话超时（消息 %s 条）", len(messages))
        return False, "AI 回答超时，请简化问题后重试。"
    except Exception as e:
        logger.error("DeepSeek 对话调用异常: %s", e)
        return False, f"请求异常: {str(e)[:200]}"

    if resp.status_code != 200:
        logger.warning("DeepSeek 返回 HTTP %s", resp.status_code)
        return False, f"AI 服务异常 (HTTP {resp.status_code})，请稍后重试。"
    return True, resp.json()["choices"][0]["message"]["content"]


@router.post("/send")
async def chat_send(req: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """发送消息给 AI 律师助手"""
    # AI 用量配额校验（受 QUOTA_ENABLED 控制，默认开启）
    if os.getenv("QUOTA_ENABLED", "true").lower() == "true" and not check_quota(user.id, "chat", db):
        logger.info("用户 %s 今日对话配额已用完", user.id)
        return {"reply": "今日 AI 对话次数已达上限（请明日再试）。", "error": True, "quota_exceeded": True}

    if not DEEPSEEK_API_KEY:
        return {"reply": "AI 助手暂未配置。请在 backend/.env 中设置 DEEPSEEK_API_KEY。", "model": "none"}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 只保留最近 20 轮对话
    for h in req.history[-20:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

    # 联网搜索：对法律相关问题先搜索再回答
    if is_legal_question(req.message) and ANYSEARCH_API_KEY:
        ctx = await web_search(f"{req.message} 法律法规 中国")
        if ctx:
            messages.append({"role": "user", "content": f"以下是从搜索引擎获取的最新参考资料，请在回答时参考这些信息（但不要直接复制，用你自己的话总结）：\n\n{ctx}"})

    messages.append({"role": "user", "content": req.message})

    ok, reply = await _deepseek_chat(messages)
    if not ok:
        return {"reply": reply, "error": True}
    return {"reply": reply, "model": "deepseek-chat"}


@router.get("/health")
async def chat_health():
    """检查 AI 服务状态"""
    return {"available": bool(DEEPSEEK_API_KEY), "model": "deepseek-chat", "search": bool(ANYSEARCH_API_KEY)}
