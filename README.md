# DocMind — 基于文档的智能检索与 AI 问答平台

> 你有没有想过，能不能丢一份文档给 AI，让它只根据这份文档来回答你的问题？DocMind 就是做这件事的。
>
> 简单来说：你上传一份 PDF/Word/Markdown 文档 → 系统自动"读懂"它 → 你提问 → AI 只根据文档内容回答你，不会瞎编。

---

## 这个项目是干什么的？

想象一下这个场景：

- 你有一份 100 页的技术规范文档
- 你想快速知道"第 3 章的性能指标是多少？"
- 传统做法：一页一页翻
- DocMind 的做法：直接问 AI，它秒回答，还告诉你答案在第几页

**核心技术叫 RAG（检索增强生成）**，原理很简单：

```
你提问
  → 系统先在文档里找到最相关的几段话（检索）
  → 把这几段话 + 你的问题一起给大模型（增强）
  → 大模型根据这些内容生成回答（生成）
```

这样做的好处是：AI 不会胡说八道，因为它只能根据你上传的文档来回答。

---

## 技术架构（用大白话讲）

```
┌─────────────────────────────────────────────────────────┐
│                        浏览器                            │
│                                                         │
│   你看到的页面（Vue 3 写的）                              │
│   - 首页、登录、上传、聊天、检索、历史                     │
│                                                         │
└────────────────────────┬────────────────────────────────┘
                         │ 你操作页面时，浏览器发请求给后端
                         │
┌────────────────────────▼────────────────────────────────┐
│                     后端服务器                            │
│                  （Python FastAPI 写的）                  │
│                                                         │
│   接收请求 → 处理业务逻辑 → 返回结果                      │
│                                                         │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│   │  SQLite   │  │  ChromaDB │  │   Ollama  │          │
│   │ 存用户、  │  │ 存文档的  │  │  大模型   │          │
│   │ 文档、历史│  │ "语义向量"│  │  (AI大脑) │          │
│   └───────────┘  └───────────┘  └───────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**用大白话解释每个技术：**

| 技术 | 是什么 | 类比 |
|------|--------|------|
| Vue 3 | 前端框架，写页面的 | 装修房子的工具 |
| FastAPI | 后端框架，处理请求的 | 餐厅的服务员，接单传菜 |
| SQLite | 轻量数据库 | 一个 Excel 表，存结构化数据 |
| ChromaDB | 向量数据库 | 一个特殊的搜索库，能按"意思"找内容 |
| Ollama | 本地大模型 | 你电脑上跑的 ChatGPT |
| JWT | 认证令牌 | 进门的门禁卡 |
| SSE | 流式输出 | 像打字机一样一个字一个字蹦出来 |

---

## 项目目录结构（每个文件是干嘛的）

```
DocMind/
│
├── .github/workflows/ci.yml     # 自动化测试配置（推代码时自动跑测试）
├── .env.example                 # 环境变量模板（告诉别人需要配置哪些参数）
├── .gitignore                   # Git 忽略规则（哪些文件不上传到 GitHub）
├── docker-compose.yml           # Docker 一键部署配置
├── README.md                    # 就是你现在看的这个文件
│
├── backend/                     # ========== 后端 ==========
│   ├── app/
│   │   ├── main.py              # 🚪 入口文件！整个后端从这里启动
│   │   │
│   │   ├── api/                 # 📡 API 接口层（定义 URL 和处理逻辑）
│   │   │   ├── auth.py          #   登录、注册、获取用户信息
│   │   │   ├── chat.py          #   普通聊天（等 AI 说完再返回）
│   │   │   ├── chat_stream.py   #   流式聊天（AI 边说边返回，打字机效果）
│   │   │   ├── documents.py     #   文档列表、详情、删除
│   │   │   ├── health.py        #   健康检查（检测服务是否正常运行）
│   │   │   ├── history.py       #   聊天历史记录
│   │   │   ├── search.py        #   知识检索（返回答案 + 引用来源）
│   │   │   └── upload.py        #   上传文档（核心！解析→分块→向量化→存储）
│   │   │
│   │   ├── core/                # ⚙️ 核心基础设施
│   │   │   ├── config.py        #   读取环境变量（数据库地址、密钥等）
│   │   │   ├── database.py      #   兼容层（重导出 db/database.py）
│   │   │   ├── logging.py       #   日志配置（记录系统运行信息）
│   │   │   ├── middleware.py    #   请求日志中间件（记录每个请求的耗时）
│   │   │   └── security.py      #   JWT 令牌工具（生成和验证门禁卡）
│   │   │
│   │   ├── db/                  # 🗄️ 数据库初始化
│   │   │   └── database.py      #   创建数据库连接、建表
│   │   │
│   │   ├── models/              # 📊 数据模型（对应数据库里的表）
│   │   │   ├── document.py      #   documents 表（存文档信息）
│   │   │   ├── chunk.py         #   document_chunks 表（存文档分块）
│   │   │   ├── chat_history.py  #   chat_histories 表（存聊天记录）
│   │   │   └── user.py          #   users 表（存用户账号密码）
│   │   │
│   │   ├── schemas/             # 📋 数据校验模型（定义 API 的输入输出格式）
│   │   │   ├── auth.py          #   注册/登录的请求和响应格式
│   │   │   ├── chat.py          #   聊天的请求和响应格式
│   │   │   ├── document.py      #   文档的响应格式
│   │   │   ├── health.py        #   健康检查的响应格式
│   │   │   ├── history.py       #   历史记录的响应格式
│   │   │   └── search.py        #   检索的请求和响应格式
│   │   │
│   │   └── services/            # 🧠 业务逻辑层（核心代码在这里）
│   │       ├── __init__.py      #   服务工厂（统一创建和管理服务实例）
│   │       ├── llm.py           #   调用 Ollama 大模型
│   │       ├── embedding.py     #   文本转向量（把文字变成数字）
│   │       ├── vector_store.py  #   向量存取（往 ChromaDB 存/取向量）
│   │       ├── rag_service.py   #   RAG 核心！组合检索+生成
│   │       ├── splitter.py      #   文本分块（把长文档切成小段）
│   │       ├── pdf_loader.py    #   解析 PDF 文件
│   │       ├── docx_loader.py   #   解析 Word 文件
│   │       ├── markdown_loader.py # 解析 Markdown 文件
│   │       ├── analysis_service.py # AI 分析（摘要、关键词等）
│   │       └── prompt.py        #   Prompt 模板（给 AI 的指令模板）
│   │
│   ├── tests/test_api.py        # 🧪 测试用例
│   ├── Dockerfile               # 🐳 后端 Docker 镜像配置
│   └── requirements.txt         # 📦 Python 依赖列表
│
└── frontend/                    # ========== 前端 ==========
    ├── src/
    │   ├── main.js              # 🚪 前端入口（创建 Vue 应用）
    │   ├── App.vue              # 🏠 根组件（导航栏 + 页面容器）
    │   ├── api/index.js         # 📡 API 封装（统一管理后端接口调用）
    │   ├── router/index.js      # 🛤️ 路由配置（URL 和页面的对应关系）
    │   └── views/               # 📄 页面组件
    │       ├── HomeView.vue     #   首页（项目介绍 + 统计 + 功能入口）
    │       ├── LoginView.vue    #   登录/注册页
    │       ├── UploadView.vue   #   上传文档页
    │       ├── ChatView.vue     #   AI 聊天页（核心！支持流式输出）
    │       ├── SearchView.vue   #   知识检索页
    │       ├── HistoryView.vue  #   历史记录页
    │       └── DocumentDetailView.vue # 文档详情页
    │
    ├── Dockerfile               # 🐳 前端 Docker 镜像配置
    ├── nginx.conf               # 🌐 Nginx 配置（反向代理）
    ├── index.html               # HTML 入口
    ├── package.json             # 📦 前端依赖列表
    └── vite.config.js           # ⚡ Vite 构建配置
```

---

## 怎么跑起来？

### 你需要先安装这些东西

1. **Python 3.9+** — 运行后端代码的
2. **Node.js 20+** — 运行前端代码的
3. **Ollama** — 本地大模型，去 https://ollama.ai 下载安装
4. 下载 AI 模型：打开终端输入 `ollama pull qwen2.5:3b`（大约 2GB，等它下完）

### 第一步：启动后端

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境（相当于给项目建一个独立的 Python 环境，不污染全局）
python -m venv .venv

# 3. 激活虚拟环境
# Mac/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 4. 安装依赖（这些是项目需要的第三方库）
pip install -r requirements.txt

# 5. 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# --reload 的意思是：你改了代码，它会自动重启，不用手动停了再启
```

看到 `Uvicorn running on http://0.0.0.0:8000` 就说明后端跑起来了！

### 第二步：启动前端（开发模式）

```bash
# 1. 新开一个终端窗口，进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动前端开发服务器
npm run dev
```

看到 `Local: http://localhost:5173/` 就说明前端跑起来了！打开浏览器访问这个地址。

> 开发模式下，前端的 `/api` 请求会自动转发到后端的 8000 端口，所以两个服务要同时跑着。

### 生产模式（只启动一个服务）

开发时前后端各跑一个服务，但部署时可以合并成一个：

```bash
# 1. 构建前端（把 Vue 代码编译成纯 HTML/CSS/JS）
cd frontend
npm install
npm run build

# 2. 把构建产物复制到后端的 static 目录
cp -r dist/* ../backend/static/

# 3. 只启动后端就行了，FastAPI 会自动托管前端页面
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

现在只需要访问 http://localhost:8000 就能用完整应用了！

---

## 后端代码详解

### 入口文件 main.py — 整个后端的大门

```python
# main.py 做了这几件事：
# 1. 创建 FastAPI 应用
# 2. 应用启动时：初始化日志 + 创建数据库表
# 3. 注册中间件：日志中间件（记录每个请求）+ CORS（允许前端跨域访问）
# 4. 注册路由：把 /api/xxx 的请求分发给对应的处理函数
# 5. 托管前端静态文件：生产模式下直接提供 Vue 构建产物
```

应用启动时执行的代码：
```python
@asynccontextmanager
async def lifespan(application: FastAPI):
    setup_logging()  # 配置日志格式
    init_db()        # 创建数据库表（如果不存在的话）
    yield            # 应用运行中...直到关闭
```

静态文件托管（让 FastAPI 同时充当前端服务器）：
```python
# 访问 / → 返回 index.html（Vue 应用的入口）
# 访问 /assets/xxx.js → 返回对应的 JS/CSS 文件
# 访问 /chat、/upload 等 → 也返回 index.html（让 Vue Router 处理前端路由）
```

### 配置文件 config.py — 所有可调参数集中管理

这个文件从环境变量（`.env` 文件或系统环境变量）中读取配置：

| 变量 | 干嘛的 | 默认值 |
|------|--------|--------|
| `APP_ENV` | 运行环境，development 会输出更多日志 | development |
| `DATABASE_URL` | 数据库在哪 | sqlite:///./docmind.db |
| `OLLAMA_BASE_URL` | Ollama 服务地址 | http://localhost:11434 |
| `DEFAULT_MODEL` | 用哪个 AI 模型 | qwen2.5:3b |
| `SECRET_KEY` | JWT 签名密钥，**生产环境必须改！** | docmind-dev-secret-... |
| `JWT_EXPIRE_MINUTES` | 登录令牌多久过期 | 1440（24小时） |

### 数据库 — 用 SQLAlchemy ORM 操作数据库

ORM 的好处：你用 Python 类来操作数据库，不用写 SQL 语句。

```python
# 定义一个表：
class Document(Base):
    __tablename__ = "documents"    # 表名
    id: Mapped[int]                # 自增主键
    file_name: Mapped[str]         # 文件名
    file_type: Mapped[str]         # 文件类型
    file_path: Mapped[str]         # 存储路径
    upload_time: Mapped[datetime]  # 上传时间

# 查询所有文档：
documents = db.query(Document).all()

# 新增一条记录：
db.add(Document(file_name="test.pdf", ...))
db.commit()
```

项目有 4 张表：

| 表名 | 存什么 | 类比 |
|------|--------|------|
| `users` | 用户账号密码 | 会员名册 |
| `documents` | 上传的文档信息 | 图书馆的图书目录 |
| `document_chunks` | 文档被切分后的文本块 | 书被拆成一页一页的 |
| `chat_histories` | 聊天记录 | 聊天记录备份 |

### API 接口 — 后端暴露给前端的 URL

所有接口都以 `/api` 开头：

| 接口 | 方法 | 干嘛的 |
|------|------|--------|
| `/api/health` | GET | 检查服务是否活着 |
| `/api/auth/register` | POST | 注册新用户 |
| `/api/auth/token` | POST | 登录获取令牌 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/upload` | POST | 上传文档 |
| `/api/documents` | GET | 文档列表 |
| `/api/documents/{id}` | GET | 文档详情 |
| `/api/documents/{id}` | DELETE | 删除文档 |
| `/api/chat` | POST | 普通聊天 |
| `/api/chat/stream` | POST | 流式聊天（打字机效果） |
| `/api/search` | POST | 知识检索 |
| `/api/history` | GET | 聊天历史 |

### 上传文档的完整流程（最核心的流程）

```
你选择一个 PDF 文件点击上传
    │
    ▼
① 校验：文件名不能为空，类型只能是 PDF/DOCX/MD，大小不能超过 100MB
    │
    ▼
② 保存：文件保存到服务器的 backend/app/uploads/ 目录
    │
    ▼
③ 记录：在数据库的 documents 表里插入一条记录
    │
    ▼
④ 解析：根据文件类型选择对应的解析器
    │   PDF → PyMuPDF 按页提取文字
    │   DOCX → python-docx 按段落提取文字
    │   MD → 正则清洗 Markdown 标签
    │
    ▼
⑤ 分块：把长文本切成 ~500 字的小段，相邻段重叠 100 字
    │   为什么要分块？因为 AI 一次看不了太长的文本，
    │   而且小块更容易精确匹配到相关内容
    │
    ▼
⑥ 向量化：用 bge-small-zh-v1.5 模型把每段文字变成 384 个数字
    │   为什么要变成数字？因为计算机只能比较数字的大小，
    │   向量化后可以计算"语义相似度"——两段话意思越接近，数字越接近
    │
    ▼
⑦ 存入 ChromaDB：把向量 + 原文 + 元数据存入向量数据库
    │
    ▼
⑧ 记录分块：在 document_chunks 表里插入每块的记录
    │
    ▼
返回成功！
```

### RAG 问答流程（另一个核心流程）

```
你输入问题："这个文档的核心结论是什么？"
    │
    ▼
① 问题向量化：把你的问题也变成 384 个数字
    │   用的是同一个模型，这样问题和文档就在同一个"空间"里了
    │
    ▼
② 向量检索：在 ChromaDB 中找到和问题最相似的 5 段文档
    │   怎么找？计算问题向量和每个文档块向量的"距离"
    │   距离越近 = 意思越相关
    │
    ▼
③ 构建 Prompt：把找到的 5 段文档 + 你的问题拼成一段完整的提示词
    │   "请基于以下内容回答问题，并给出引用来源。
    │    来源段落1：xxxxx
    │    来源段落2：xxxxx
    │    ...
    │    问题：这个文档的核心结论是什么？
    │    回答："
    │
    ▼
④ AI 生成回答：把 Prompt 发给 Ollama 大模型
    │   大模型只根据你提供的文档内容来回答，不会瞎编
    │   流式模式下，AI 边想边说，一个字一个字返回
    │
    ▼
⑤ 保存历史：把问题和回答存入 chat_histories 表
    │
    ▼
返回回答！
```

### 认证系统 — JWT 令牌

```
注册/登录流程：
  用户输入用户名密码 → 后端验证 → 生成 JWT 令牌 → 返回给前端

每次请求：
  前端自动在请求头带上令牌 → 后端验证令牌 → 通过则处理请求

令牌过期：
  默认 24 小时后过期 → 前端收到 401 错误 → 自动跳转到登录页
```

JWT 令牌就像一张加密的身份证，里面存着用户名和过期时间，别人无法伪造（除非知道密钥）。

### 日志中间件 — 记录每个请求

每个请求都会自动记录一行日志：

```
2026-07-14 18:32:24 | INFO | access | POST /api/chat/stream 200 1523.4ms request_id=a1b2c3d4
```

这行日志告诉你：什么时间、什么方法、访问了哪个接口、返回了什么状态码、花了多少毫秒、请求 ID 是什么。

---

## 前端代码详解

### 技术栈

| 技术 | 干嘛的 |
|------|--------|
| Vue 3 | 前端框架，用组合式 API 写组件 |
| Vite | 构建工具，开发时热更新超快 |
| Element Plus | UI 组件库，提供按钮、表单、弹窗等现成组件 |
| Vue Router | 路由管理，URL 和页面的对应关系 |
| Pinia | 状态管理（本项目主要用 localStorage，Pinia 预留） |
| Axios | HTTP 客户端，发请求给后端 |

### 路由 — URL 和页面的对应关系

| URL | 页面 | 需要登录？ |
|-----|------|-----------|
| `/` | 首页 | 是 |
| `/login` | 登录/注册 | 否（已登录反而进不来） |
| `/upload` | 上传文档 | 是 |
| `/chat` | AI 聊天 | 是 |
| `/search` | 知识检索 | 是 |
| `/history` | 历史记录 | 是 |
| `/documents/:id` | 文档详情 | 是 |

导航守卫的逻辑：
- 没登录 → 任何页面都跳转到登录页
- 已登录 → 登录页跳转到首页

### API 封装 — 统一管理后端接口调用

`api/index.js` 做了两件重要的事：

**1. 请求拦截器** — 每次发请求自动带上 JWT 令牌：
```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

**2. 响应拦截器** — 令牌过期自动跳转登录页：
```javascript
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)
```

### 聊天页面 — 最复杂的前端组件

聊天页面用了 `fetch` 而不是 `axios` 来调用流式接口，因为：

- `axios` 会等数据全部到齐再给你 → 你看到的是等很久然后一次性出现
- `fetch` 的 `response.body.getReader()` 可以逐块读取 → 实现打字机效果

核心代码逻辑：
```javascript
// 1. 用 fetch 发请求
const response = await fetch(url, { method: 'POST', body: ... })

// 2. 获取数据流的读取器
const reader = response.body.getReader()

// 3. 循环读取每一块数据
while (true) {
  const { done, value } = await reader.read()
  if (done) break  // 数据读完了

  // 4. 解码二进制数据为文本
  const text = decoder.decode(value)

  // 5. 解析 SSE 格式（每行以 "data: " 开头）
  // 6. 把每个字追加到聊天气泡里 → 打字机效果！
}
```

---

## Docker 部署 — 一键上线

Docker 的作用：把你的应用打包成一个"集装箱"，在任何服务器上都能跑，不用操心环境问题。

```bash
# 一键启动所有服务
docker-compose up --build -d

# 查看运行状态
docker-compose ps

# 停止所有服务
docker-compose down
```

`docker-compose.yml` 定义了两个服务：
- **backend**：后端服务，暴露 8000 端口，通过 `host.docker.internal` 访问宿主机的 Ollama
- **frontend**：前端服务，Nginx 托管，暴露 80 端口，把 `/api` 请求转发给后端

---

## CI/CD — 自动化测试

`.github/workflows/ci.yml` 配置了 GitHub Actions：

每次你往 GitHub 推代码，它会自动：
1. 跑后端测试（`pytest`）
2. 构建前端（`npm run build`）

如果测试失败，你会收到邮件通知，避免把有问题的代码部署上线。

---

## 测试

```bash
cd backend
python -m pytest tests/ -v
```

10 个测试用例覆盖了：
- 健康检查是否正常
- 注册/登录流程是否正确
- 重复注册是否被拒绝
- 密码错误是否返回 401
- 带令牌/不带令牌访问受保护接口
- 空问题是否被拒绝

---

## 环境变量

先复制模板：`cp .env.example .env`

| 变量 | 说明 | 必须改？ |
|------|------|---------|
| `SECRET_KEY` | JWT 签名密钥 | **生产环境必须改成随机字符串！** |
| `OLLAMA_BASE_URL` | Ollama 地址 | Docker 部署时需要改 |
| `DEFAULT_MODEL` | AI 模型名称 | 换模型时改 |
| 其他 | 都有合理默认值 | 一般不用改 |

> ⚠️ `.env` 文件在 `.gitignore` 里，不会被提交到 GitHub，所以你的密钥是安全的。
> `.env.example` 是模板，只有占位符，提交上去没问题。