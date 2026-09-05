"""合同审查 + 案件智能分析"""
import os
import uuid
import logging
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Case, CaseFile, User
from auth import get_current_user
from .quota import check_quota
# 复用 citation.render_citation_section：依赖其"法条库缺失时返回空串"的降级约定
from .citation import render_citation_section
# 复用 anysearch.search：依赖其"未配 Key 或失败时返回空串"的降级约定
from .anysearch import search as web_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contract", tags=["合同审查"])

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
ANYSEARCH_API_KEY = os.environ.get("ANYSEARCH_API_KEY", "")

CONTRACT_API_KEY = os.environ.get("CONTRACT_API_KEY", DEEPSEEK_API_KEY)
CASE_ANALYSIS_API_KEY = os.environ.get("CASE_ANALYSIS_API_KEY", DEEPSEEK_API_KEY)

# 与 files.py 保持一致的上传根目录，案件文件统一落盘存储
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(Path(__file__).parent.parent / "uploads"))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB

if not DEEPSEEK_API_KEY:
    logger.warning("DEEPSEEK_API_KEY 未配置，合同审查和案件分析功能不可用")


async def _ask_deepseek(system_prompt: str, user_content: str, api_key: str = None, max_tokens: int = 4000) -> str:
    """通用 DeepSeek 调用（异步）；被本模块和 law_search.py 复用，改签名需同步 law_search.py"""
    key = api_key or DEEPSEEK_API_KEY
    if not key:
        return "AI 功能未配置，请在 .env 中设置 API Key"

    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        # 调低温度提升条款覆盖的稳定性；长度由调用方分块控制，这里不再硬截断
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=200) as client:
        resp = await client.post(
            DEEPSEEK_URL, json=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
    if resp.status_code != 200:
        return f"AI 调用失败: {resp.status_code}"
    return resp.json()["choices"][0]["message"]["content"]


def _read_case_file_text(cf: CaseFile, limit: int = 5000) -> str:
    """从磁盘读取已上传的案件文件文本（与 files.py 存储约定一致）"""
    abs_path = os.path.join(UPLOAD_DIR, cf.file_path or "")
    ext = Path(cf.file_name or "").suffix.lower()
    if not abs_path or not os.path.exists(abs_path):
        return ""
    try:
        if ext == ".pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(abs_path)
            text = ""
            for page in reader.pages[:10]:  # 最多读10页
                text += (page.extract_text() or "") + "\n"
            return text[:limit]
        if ext in (".txt", ".md"):
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as fh:
                return fh.read()[:limit]
    except Exception as e:
        return f"(文件读取失败: {str(e)[:50]})"
    return ""


# ========== 合同审查 ==========

CONTRACT_SYSTEM_PROMPT = """你是一位资深合同审查律师。请对下面的合同进行系统、逐条、全面的审查。

## 审查步骤（必须严格遵循）
1. 先通读全文，列出合同出现的所有条款编号（如"第一条""第二条 2.2""第十条 10.1"等）。
2. 逐条对照下列【固定风险核查清单】进行检查，凡涉及的必须指出，并引用对应《民法典》条款（如第 496、497、585 条等）：
   - 主体资格：当事人名称、统一社会信用代码、法定代表人、地址是否齐全，主体是否适格
   - 标的与范围：标的、数量、技术标准、功能清单是否明确
   - 价款与支付：金额、付款节点、支付条件、发票是否清晰；违约金/赔偿金是否与对方【对等】、是否过高（日 1% 通常过高）
   - 履行期限与验收：交付/验收期限、标准、程序、修改次数是否明确
   - 知识产权：背景知识产权与新增成果归属、使用许可范围、侵权保证
   - 保密：保密义务是否【双向】约束双方，保密信息范围与例外是否明确
   - 违约：违约责任是否对等，免责/责任限制条款是否单方排除主要责任（格式条款无效风险）
   - 不可抗力：列举是否过窄（仅地震、洪水不够），是否约定通知义务与时限、持续过久的处理
   - 争议解决：仲裁与诉讼是否冲突、仲裁机构/管辖法院是否明确、是否约定在对方所在地增加维权成本
   - 解除/终止：解除情形、自动续约、提前终止权是否约定
   - 合规：是否涉及个人信息/数据合规、资质许可
   - 其他：最终解释权、免责过宽、违约金可能远超实际损失等
3. 指出合同【缺失】的常见必要条款。
4. 给出每条风险的修改建议（含可替换条款表述）。

## 输出要求（Markdown，结构固定不可省略）
- 一、风险点识别（表格：序号/条款位置/风险描述/严重程度 高|中|低，每条必须注明《民法典》依据）
- 二、关键条款分析（分节，逐类评析）
- 三、缺失条款提示（表格）
- 四、修改建议汇总
- 五、综合评分（A/B/C/D 级 + 一句话总结）
- 末尾附"条款覆盖核查"：列出原文所有条款编号，逐条标注【已审查】或【未审查】。

务必逐条走过，不要遗漏任何条款；凡有风险的条款必须给出法条依据。"""

# 长合同分块时，单块仅做风险提取（不出评分/缺失汇总）
CONTRACT_CHUNK_PROMPT = """你是一位合同审查律师。下面是一份合同中的一段文本（可能只是部分条款）。请仅就你看到的条款，按以下格式输出风险分析，不要写综合评分，不要写缺失条款汇总：

- 风险点：<描述>
- 条款位置：<如 第六条 6.1>
- 严重程度：高/中/低
- 法条依据：<《民法典》第X条>
- 修改建议：<具体表述>

若本段无明显风险，输出"本段未发现明显风险"。"""

# 分块结果合并为一份完整报告
CONTRACT_SYNTH_PROMPT = """你是一位资深合同审查律师。下面是同一份合同被分多段审查后得到的风险分析片段（可能含重复）。请：
1. 去重合并；
2. 按统一格式整理成一份完整审查报告（Markdown）：
   - 一、风险点识别（表格）
   - 二、关键条款分析
   - 三、缺失条款提示
   - 四、修改建议汇总
   - 五、综合评分（A/B/C/D 级 + 一句话总结）
3. 末尾附"条款覆盖核查"：列出原文主要条款编号并标注【已审查/未审查】。

保持专业、准确，引用《民法典》条款。"""

# 二次自检：对照原文条款清单，找出未被覆盖的条款
CONTRACT_SELFCHECK_PROMPT = """你是一位严谨的合同审查质检员。请对照【合同原文】的条款清单与【已生成审查报告】，逐条核对：

1. 列出原文出现的所有主要条款编号（如第一条、第二条 2.2、第十条 10.1 等）；
2. 对每条，判断审查报告中是否已有对应风险点覆盖（无论结论是否有风险，只要被审查过即算覆盖）；
3. 列出【未被任何风险点覆盖】的条款编号，并说明为何可能遗漏；
4. 若全部覆盖，写明"无遗漏"。

输出 Markdown，简明。"""

CHUNK_SIZE = 6000
CHUNK_OVERLAP = 600


async def _chunked_review(content: str, api_key: str, type_hint: str = "") -> str:
    """合同审查主入口：短合同单次调用；长合同分块审查后合并，避免后半截被截断漏审。"""
    if len(content) <= 12000:
        # 详细审查报告较长，提高输出 token 上限避免后半截（缺失条款/修改建议/综合评分）被截断
        return await _ask_deepseek(CONTRACT_SYSTEM_PROMPT, content, api_key, max_tokens=8000)
    chunks = []
    start = 0
    n = len(content)
    while start < n:
        end = min(start + CHUNK_SIZE, n)
        chunks.append(content[start:end])
        if end == n:
            break
        start = end - CHUNK_OVERLAP
    parts = []
    for i, ch in enumerate(chunks, 1):
        hint = (
            f"\n（以下为合同第 {i}/{len(chunks)} 段，请仅就本段出现的条款作分析，"
            f"暂不打分、不出缺失条款汇总，按 风险点/条款位置/严重程度/法条依据/修改建议 输出。"
            f"用户要求：{type_hint or '全面审查'}）"
        )
        parts.append(await _ask_deepseek(CONTRACT_CHUNK_PROMPT, ch + hint, api_key, max_tokens=3000))
    merged = "\n\n".join(parts)
    synth_user = f"【分块审查片段】\n{merged}\n\n用户整体要求：{type_hint or '全面审查'}"
    return await _ask_deepseek(CONTRACT_SYNTH_PROMPT, synth_user, api_key, max_tokens=5000)


async def _self_check(original: str, review_text: str, api_key: str) -> str:
    """二次质检：找出审查报告中未被任何风险点覆盖的原始条款。"""
    user = (
        f"【合同原文】\n{original}\n\n"
        f"【已生成审查报告】\n{review_text}\n\n请逐条核对原始条款的覆盖情况。"
    )
    try:
        return await _ask_deepseek(CONTRACT_SELFCHECK_PROMPT, user, api_key, max_tokens=1500)
    except Exception as e:
        # 自检是增强步骤，失败不阻断审查报告返回
        logger.warning("合同审查自检失败: %s", e)
        return ""


class ContractReviewReq(BaseModel):
    content: str  # 合同文本
    review_type: str = "full"  # full / clauses_only / risks_only


@router.post("/review")
async def review_contract(req: ContractReviewReq, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """审查合同文本"""
    if os.getenv("QUOTA_ENABLED", "true").lower() == "true":
        if not check_quota(user.id, "contract", db):
            return {"result": "今日 AI 合同审查次数已达上限，请明日再试。", "quota_exceeded": True}

    if not req.content.strip():
        return {"error": "请提供合同文本"}

    type_hint = ""
    if req.review_type == "clauses_only":
        type_hint = "\n请重点分析关键条款，不需要综合评分。"
    elif req.review_type == "risks_only":
        type_hint = "\n请仅列出风险点和修改建议，不需要完整分析。"

    # 联网搜索同类合同审查要点和案例
    search_ctx = ""
    if ANYSEARCH_API_KEY:
        search_ctx = await web_search(f"{req.content[:100]} 合同审查 风险点 法律依据")

    user_content = req.content + type_hint
    if search_ctx:
        user_content = f"【以下为网络搜索的合同审查参考信息，请结合这些信息进行审查】\n{search_ctx}\n\n【合同正文】\n{user_content}"

    # 分块审查（长合同防截断漏审）+ 二次自检（找出未覆盖条款）
    result = await _chunked_review(user_content, CONTRACT_API_KEY, type_hint)
    selfcheck = await _self_check(req.content, result, CONTRACT_API_KEY)
    if selfcheck and not selfcheck.startswith("AI 调用失败"):
        result = result + "\n\n---\n\n## 六、审查覆盖自检\n\n" + selfcheck

    # 法条引用核验：自动比对《民法典》权威库，标出虚构条号（库缺失时优雅跳过）
    citation_section = render_citation_section(result)
    if citation_section:
        result = result + "\n\n---\n\n" + citation_section

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

    if os.getenv("QUOTA_ENABLED", "true").lower() == "true":
        if not check_quota(current_user.id, "case_analysis", db):
            return {"case_id": case_id, "result": "今日 AI 案件分析次数已达上限，请明日再试。", "quota_exceeded": True}

    # 收集案件信息和文件内容
    analysis_text = f"案件类型：{case.case_type or '未知'}\n"
    analysis_text += f"原告：{case.plaintiff or ''}\n"
    analysis_text += f"被告：{case.defendant or ''}\n"
    analysis_text += f"法院：{case.court_name or '未知'}\n"
    analysis_text += f"案件描述：{case.description or '无'}\n"
    analysis_text += f"标的额：{case.subject_amount or 0}元\n\n"

    # 读取上传的文件（从磁盘，与 files.py 一致）
    files = db.query(CaseFile).filter(CaseFile.case_id == case_id).all()
    if files:
        analysis_text += "=== 已上传文件内容 ===\n\n"
        for f in files:
            text = _read_case_file_text(f)
            if text:
                analysis_text += f"--- {f.file_name} ---\n{text}\n\n"

    if not DEEPSEEK_API_KEY:
        return {"error": "AI 功能未配置"}

    # 联网搜索类似案件判例和法律依据
    if ANYSEARCH_API_KEY:
        search_query = f"{case.case_type or ''} {case.plaintiff or ''} {case.defendant or ''} 判例 法律依据".strip()
        if len(search_query) > 10:
            search_ctx = await web_search(search_query)
            if search_ctx:
                analysis_text = f"【以下为网络搜索的同类案件参考】\n{search_ctx}\n\n{analysis_text}"

    result = await _ask_deepseek(CASE_ANALYSIS_PROMPT, analysis_text[:12000], CASE_ANALYSIS_API_KEY)

    # 保存分析结果到案件备注
    try:
        existing_note = case.notes or ""
        case.notes = f"{existing_note}\n\n--- AI 智能分析 ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n{result}"
        db.commit()
    except Exception as e:
        logger.warning("保存案件分析结果失败 case=%s: %s", case_id, e)

    return {"case_id": case_id, "result": result}


# ========== 文件上传（复用 files.py 的落盘存储约定） ==========

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
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(400, f"文件超过大小限制（{MAX_UPLOAD_SIZE // 1024 // 1024}MB）")

    safe_fname = os.path.basename(file.filename or "file")
    ext = Path(safe_fname).suffix.lower()
    if not ext:
        raise HTTPException(400, "无法识别文件类型，请确保文件名包含后缀")

    unique_name = f"{uuid.uuid4()}{ext}"
    relative_path = f"cases/{case_id}/{unique_name}"
    absolute_path = os.path.join(UPLOAD_DIR, relative_path)
    Path(absolute_path).parent.mkdir(parents=True, exist_ok=True)
    with open(absolute_path, "wb") as fh:
        fh.write(content)

    # 简单类型推断
    file_type = "other"
    low = (file.filename or "").lower()
    if any(kw in low for kw in ["证据", "evidence", "proof"]):
        file_type = "evidence"
    elif any(kw in low for kw in ["判决", "judgment", "裁定", "ruling"]):
        file_type = "judgment"
    elif any(kw in low for kw in ["委托", "entrust", "授权", "authorization", "代理"]):
        file_type = "entrustment"

    cf = CaseFile(
        case_id=case_id,
        user_id=current_user.id,
        file_name=file.filename,
        file_type=file_type,
        file_size=len(content),
        file_path=relative_path,
        mime_type=file.content_type or "application/octet-stream",
    )
    db.add(cf)
    db.commit()
    return {"id": cf.id, "filename": cf.file_name, "size": len(content)}
