# DocMind

DocMind 是一个面向文档分析的 AI 平台骨架项目，当前阶段仅完成项目初始化与可运行的开发环境搭建。

## 项目结构

- backend：FastAPI 后端服务
- frontend：Vue 3 + Vite 前端应用

## 后端启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 说明

当前版本不包含业务功能，只提供统一的工程化目录结构与可运行的启动入口。
