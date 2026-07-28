"""AI 法律对话助手"""
import os, json, httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

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


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # [{role: "user"/"assistant", content: "..."}]


@router.post("/send")
async def chat_send(req: ChatRequest, user=Depends(get_current_user)):
    """发送消息给 AI 律师助手"""
    if not DEEPSEEK_API_KEY:
        return {
            "reply": "AI 助手暂未配置。请在 backend/.env 中设置 DEEPSEEK_API_KEY。",
            "model": "none",
        }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 只保留最近 20 轮对话
    for h in req.history[-20:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    
    messages.append({"role": "user", "content": req.message})

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                DEEPSEEK_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 2048,
                },
            )
            data = resp.json()

        if resp.status_code != 200:
            return {"reply": f"AI 服务异常 (HTTP {resp.status_code})，请稍后重试。", "error": True}

        content = data["choices"][0]["message"]["content"]
        return {"reply": content, "model": "deepseek-chat"}

    except httpx.TimeoutException:
        return {"reply": "AI 回答超时，请简化问题后重试。", "error": True}
    except Exception as e:
        return {"reply": f"请求异常: {str(e)[:200]}", "error": True}


@router.get("/health")
async def chat_health():
    """检查 AI 服务状态"""
    return {"available": bool(DEEPSEEK_API_KEY), "model": "deepseek-chat"}
