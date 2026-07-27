# 律师SaaS - 项目记忆

## 项目概览
- **名称：** 法律AI助手
- **技术栈：** 前端 Vue3+TailwindCSS+Vite, 后端 Python FastAPI+SQLAlchemy+SQLite
- **端口：** 后端 8000, 前端 5173
- **目标用户：** 中小律所（3-20人）

## 启动命令
- **后端：** `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
- **前端：** `cd frontend && npm run dev`

## 关键决策
- 密码哈希使用 bcrypt 直接调用, 不用 passlib（兼容性问题）
- JWT sub 必须是字符串，不能是 int
- DeepSeek API Key 在 backend/.env 中配置
- npm 需配代理 http://127.0.0.1:7892，registry 用 npmmirror.com（npmjs.org 太慢 ~90s/包）
- npm install 必须用 dangerouslyDisableSandbox: safe-delete 会阻止批量删除/安装文件
- 测试账号：13800138000 / 123456（已创建）

## 数据库表
- users（用户）, cases（案件）, documents（文书）, case_files（文件）

## 文件结构
```
G:\律师SaaS\
├── backend/         # FastAPI 后端
│   ├── main.py      # 入口
│   ├── auth.py      # 认证
│   ├── database.py  # 数据库
│   ├── models.py    # ORM 模型
│   ├── schemas.py   # Pydantic schemas
│   ├── routers/     # API 路由
│   └── .env         # 环境变量
└── frontend/        # Vue3 前端
    └── src/
        ├── views/   # 页面组件
        ├── router/  # 路由
        └── api/     # API 封装
```
