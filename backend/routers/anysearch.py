"""AnySearch 联网搜索封装：chat / contract 等模块共用的搜索入口。

调用 AnySearch 的 MCP 接口做网页检索，返回清洗后的纯文本上下文（截断 2000 字）。
未配置 ANYSEARCH_API_KEY 或调用失败时返回空串——调用方据此跳过搜索增强，
不阻断主流程（搜索只是增强能力）。
"""
import os
import re
import logging

import httpx

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("ANYSEARCH_API_KEY", "")
URL = "https://api.anysearch.com/mcp"

_MAX_TEXT = 2000  # 搜索上下文最大长度，控制 token 消耗


async def search(query: str, max_results: int = 5) -> str:
    """检索 AnySearch，返回清洗后的文本；失败/未配 Key 返回空串，不抛错。"""
    if not API_KEY:
        return ""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": "search", "arguments": {"query": query, "max_results": max_results}},
                    "id": 1,
                },
            )
        content = (resp.json().get("result", {}).get("content") or [{}])[0]
        if content.get("type") != "text":
            return ""
        text = re.sub(r"\*\*URL\*\*:.*\n?", "", content["text"])  # 去掉 **URL**: 行
        text = re.sub(r"\n{3,}", "\n\n", text)  # 压掉连续空行
        return text[:_MAX_TEXT]
    except Exception as e:
        logger.warning("AnySearch 搜索失败 query=%r: %s", query[:50], e)
        return ""
