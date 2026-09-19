# Lexi — 面向律所的法律 AI SaaS

> 律师的案件管理、合同审查、AI 咨询原本散在三四个工具里，Lexi 把它们收进一个工作台。

[![Tests](https://github.com/qiuli55/SaaS/actions/workflows/tests.yml/badge.svg)](https://github.com/qiuli55/SaaS/actions/workflows/tests.yml)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI%200.115-009688)]()
[![Vue](https://img.shields.io/badge/frontend-Vue%203.5-42b883)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)]()

**在线体验**：[https://lexi.qiuli55.top](https://lexi.qiuli55.top) —— 已生产部署，可直接打开

<!-- 截图待补：建议放一张案件详情页或合同审查页，路径 docs/screenshots/case-detail.png -->

## 这是什么

前后端分离、可安装为 PWA 的垂直 SaaS，覆盖律师与律所团队的日常工作流。后端 FastAPI 按领域拆成 16 个 router，前端 Vue 3；AI 能力（DeepSeek）嵌入合同审查、案件分析、法律咨询三个高频场景。

## 架构

```
浏览器 / PWA
    │  HTTPS
    ▼
Nginx ─── 静态资源（Vue dist）
    │  /api/ → 127.0.0.1:8001
    ▼
FastAPI（16 router）── JWT 鉴权 · slowapi 限流 · 每日配额校验
    │
    ├── SQLAlchemy → SQLite
    └── httpx ──→ DeepSeek（对话 / 合同审查 / 案件分析）
              └─→ AnySearch（法律问题联网检索）
```

## 核心功能

- **合同智能审查**：上传合同 → DeepSeek 逐项审查 → 法条引用渲染；词条库缺失时优雅降级，不影响主流程
- **案件智能分析**：案件材料结合联网检索（AnySearch）辅助分析
- **AI 法律咨询**：带律师系统提示词的对话助手，引用具体法条、给出可执行步骤
- **案件 / 客户 / 文书 / 日程管理**：立案、材料上传（默认 50MB，可配置）、文书生成与历史版本
- **团队协作**：多团队管理、邀请码加入体系
- **认证与配额**：JWT 登录、短信验证码注册、接口限流、按日配额（免费版 50 次/天，付费按套餐）

## 关键技术难点

1. **AI 依赖全链路降级**：三个 AI 入口各自独立降级——未配 `DEEPSEEK_API_KEY` 时返回友好提示而非 500；法条词条库加载失败返回 `None`，跳过引用渲染；AnySearch 未配 Key 或请求失败返回空串。任一外部依赖挂掉，主流程不受影响，演示不会崩。
2. **配额统计的时区一致性**：`created_at` 按 UTC 落库，配额却按自然日（东八区）计算，直接比较会差 8 小时——每天 00:00–08:00 之间配额会被错误重置。修复方式是统一用 `func.date(created_at, "localtime")` 归到本地日期。
3. **外部 API 的超时与异常隔离**：DeepSeek 调用设 45s 超时，并按「超时 / HTTP 错误 / 请求异常」分类捕获、返回不同文案，避免一次外部抖动拖垮接口。

## 技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 后端 | FastAPI 0.115 + SQLAlchemy 2.0 | 异步框架 + 自动生成 OpenAPI 文档；按领域拆 router，便于并行开发 |
| 数据库 | SQLite | 单机部署零运维；ORM 层做隔离，换 PostgreSQL 只需改连接串 |
| 鉴权 | python-jose (JWT) + bcrypt | 无状态鉴权，密码加盐哈希存储 |
| 限流 | slowapi | 生产 200 次/天 + 60 次/小时；测试环境自动放宽 |
| 前端 | Vue 3.5 + Vite 6 + Tailwind 3.4 | 构建快、可安装为 PWA |
| AI | DeepSeek + AnySearch | 对话 / 审查 / 分析 + 联网检索 |

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env      # 填 DEEPSEEK_API_KEY、短信服务密钥
uvicorn main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 部署

`deploy/` 目录提供生产部署方案：前端 dist 构建产物、nginx 配置、Windows 一键 `setup.bat`、SSL 配置文档 [SSL-SETUP.md](deploy/SSL-SETUP.md)。

线上环境：`https://lexi.qiuli55.top`，Nginx 443 按域名分流 → `127.0.0.1:8001`。

## 测试

```bash
cd backend && pytest
```

CI（GitHub Actions）在每次 push 与 PR 时自动执行，59 项全部通过。按文件拆分：

| 文件 | 项数 | 覆盖范围 |
|---|---|---|
| `tests/test_api.py` | 38 | 认证 / 案件 / 日程 / 客户 / 文件上传 / 改密 |
| `tests/test_billing.py` | 10 | 套餐 / 订单 / 模拟支付 / 取消订阅权益保留 / 用量限额 |
| `tests/test_citation.py` | 11 | 中文数字转换 / 法条条号核验 / 检索接口 |

## 许可证

私有项目，未授权转载。
