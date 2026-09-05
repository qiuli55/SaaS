# Lexi — 面向律所的法律 AI SaaS 平台

> 把案件管理、合同审查、AI 法律咨询放进同一个工作台，律师的事在系统里办完。

[![Tests](https://img.shields.io/badge/tests-38%20passed-brightgreen)]()
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)]()
[![Vue 3](https://img.shields.io/badge/frontend-Vue%203-42b883)]()

## 这是什么

**Lexi** 是一个面向律师/律所团队的垂直 SaaS，前后端分离 + PWA，覆盖律所日常核心工作流，并把 AI 能力（DeepSeek）嵌进合同审查、案件分析和法律咨询三个高频场景。

## 核心功能

| 模块 | 说明 |
|---|---|
| 📁 案件管理 | 立案 / 编辑 / 详情 / 案件文件上传（50MB 上限），案件材料统一落盘 |
| 👥 客户管理 | 客户档案与详情视图 |
| 📄 合同智能审查 | 上传合同 → AI 逐项审查，支持法条引用渲染（法条库缺失时优雅降级） |
| ⚖️ 案件智能分析 | 案件材料 + 联网检索（AnySearch）辅助分析 |
| 🤖 AI 法律咨询 | 带律师系统提示词的对话助手：引用具体法条、给可执行步骤、SSE 流式输出 |
| 📝 文书管理 | 文书生成 / 编辑 / 历史版本查询 |
| 📅 日程日历 | 日历视图管理排期 |
| 🏢 团队协作 | 多团队 / 成员邀请（邀请码体系）/ 团队详情 |
| 🔍 律所名录 | 内置全国律所数据库（爬虫采集 + 清洗入库），模糊搜索 |
| 🔐 认证与配额 | JWT 登录 + 阿里云短信验证码注册 + 接口限流 + 用户配额管理 |

## 技术栈

- **后端**：Python FastAPI + SQLAlchemy + SQLite，按领域拆分 13 个 router 模块
- **前端**：Vue 3 + Vite + Tailwind CSS，PWA（可安装到桌面/手机）
- **AI**：DeepSeek API（对话 / 合同审查 / 案件分析），AnySearch 联网检索
- **基础设施**：阿里云短信认证、JWT、接口限流（limiter）

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env   # 配置 DEEPSEEK_API_KEY、短信服务密钥
uvicorn main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

`deploy/` 目录提供生产部署方案：前端 dist 构建产物、Windows 一键 `setup.bat`、SSL 配置文档（[SSL-SETUP.md](deploy/SSL-SETUP.md)）。

## 工程化

- pytest 后端测试 38 项全通过（含短信/邀请码注册流程适配）
- 所有 AI 依赖均有降级约定：未配 Key 时功能不可用但系统不崩
- 上传文件统一落盘管理，尺寸限制可配置

## 许可证

私有项目，未授权转载。
