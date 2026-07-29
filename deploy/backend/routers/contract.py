"""合同审查 + 案件智能分析"""
import io, json, httpx, os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Case, CaseFile, User
from auth import get_current_user

router = APIRouter(prefix="/api/contract", tags=["合同审查"])

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

if not DEEPSEEK_API_KEY:
    print("[WARN] DEEPSEEK_API_KEY 未配置，合同审查和案件分析功能不可用")


def _ask_deepseek(system_prompt: str, user_content: str) -> str:
    """通用 DeepSeek 调用"""
    if not DEEPSEEK_API_KEY:
        return "AI 功能未配置，请在 .env 中设置 DEEPSEEK_API_KEY"

    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content[:12000]},  # 限制长度
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }
    resp = httpx.post(DEEPSEEK_URL, json=body, headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }, timeout=90)
    if resp.status_code != 200:
        return f"AI 调用失败: {resp.status_code}"
    return resp.json()["choices"][0]["message"]["content"]


# ========== 合同审查 ==========

CONTRACT_SYSTEM_PROMPT = """你是一位资深合同审查律师。用户会给你合同文本或条款，请你从以下维度进行审查：

1. **风险点识别**：逐条列出合同中存在的法律风险，标注严重程度（高/中/低）
2. **关键条款分析**：对违约责任、争议解决、保密、知识产权、付款条件等核心条款逐一评析
3. **缺失条款提示**：指出合同缺少哪些常见但必要的条款
4. **修改建议**：对每个风险点给出具体的修改建议或替代条款表述
5. **综合评分**：最后给出合同整体风险评级（A/B/C/D级）和一句话总结

输出格式用 Markdown，结构清晰，分点列举。"""


class ContractReviewReq(BaseModel):
    content: str  # 合同文本
    review_type: str = "full"  # full / clauses_only / risks_only


@router.post("/review")
async def review_contract(req: ContractReviewReq, user=Depends(get_current_user)):
    """审查合同文本"""
    if not req.content.strip():
        return {"error": "请提供合同文本"}
    
    type_hint = ""
    if req.review_type == "clauses_only":
        type_hint = "\n请重点分析关键条款，不需要综合评分。"
    elif req.review_type == "risks_only":
        type_hint = "\n请仅列出风险点和修改建议，不需要完整分析。"

    result = _ask_deepseek(CONTRACT_SYSTEM_PROMPT, req.content + type_hint)
    return {"result": result}


# ========== 案件智能分析 ==========

CASE_ANALYSIS_PROMPT = """你是一位经验丰富的诉讼律师助手。请基于以下案件材料和证据文本，进行结构化分析。

请按以下四个维度输出分析结果，用 Markdown 格式：

## 时间线梳理
按时间顺序列出所有关键事件日期和事件内容。格式：YYYY-MM-DD 事件描述

## 主体关系分析
列出案件涉及的所有主体（当事人、公司、证人、担保人等），描述他们之间的法律关系（如：买卖合同当事方、担保关系、委托代理关系等）

## 案件事实概述
用200字以内的简洁语言概括案件核心事实

## 初步争议焦点
列出3-5个核心法律争议点，每个争议点用一句话概括

注意：
- 从材料中严格提取，不要编造不存在的信息
- 如果某个维度信息不足，请注明"材料中未体现"
- 使用中文输出"""


@router.post("/cases/{case_id}/analyze")
async def analyze_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI 分析案件：读取上传的文件+案件描述，生成时间线/关系图/争议分析"""
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()
    if not case:
        raise HTTPException(404, "案件不存在")

    # 收集案件信息和文件内容
    analysis_text = f"案件类型：{case.case_type or '未知'}\n"
    analysis_text += f"原告：{case.plaintiff or ''}\n"
    analysis_text += f"被告：{case.defendant or ''}\n"
    analysis_text += f"法院：{case.court_name or '未知'}\n"
    analysis_text += f"案件描述：{case.description or '无'}\n"
    analysis_text += f"标的额：{case.subject_amount or 0}元\n\n"

    # 读取上传的文件
    files = db.query(CaseFile).filter(CaseFile.case_id == case_id).all()
    if files:
        analysis_text += "=== 已上传文件内容 ===\n\n"
        for f in files:
            if f.filename.lower().endswith('.pdf'):
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(io.BytesIO(f.file_data))
                    pdf_text = ""
                    for page in reader.pages[:10]:  # 最多读10页
                        pdf_text += (page.extract_text() or "") + "\n"
                    analysis_text += f"--- {f.filename} ---\n{pdf_text[:5000]}\n\n"
                except Exception as e:
                    analysis_text += f"--- {f.filename} (PDF读取失败: {str(e)[:50]}) ---\n\n"
            elif f.filename.lower().endswith(('.txt', '.md')):
                try:
                    analysis_text += f"--- {f.filename} ---\n{f.file_data.decode('utf-8', errors='ignore')[:5000]}\n\n"
                except:
                    pass

    if not DEEPSEEK_API_KEY:
        return {"error": "AI 功能未配置"}

    result = _ask_deepseek(CASE_ANALYSIS_PROMPT, analysis_text[:12000])

    # 保存分析结果到案件备注
    try:
        existing_note = case.notes or ""
        case.notes = f"{existing_note}\n\n--- AI 智能分析 ({__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n{result}"
        db.commit()
    except:
        pass

    return {"case_id": case_id, "result": result}


# ========== 文件上传（复用或补充） ==========

@router.post("/cases/{case_id}/upload")
async def upload_case_file(
    case_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传案件文件（用于分析）"""
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()
    if not case:
        raise HTTPException(404, "案件不存在")

    content = await file.read()
    cf = CaseFile(
        case_id=case_id,
        filename=file.filename,
        file_data=content,
        file_type=file.content_type or "application/octet-stream",
    )
    db.add(cf)
    db.commit()
    return {"id": cf.id, "filename": cf.filename, "size": len(content)}
