# DocMind — 基于文档的智能检索与 AI 问答平台

> DocMind 是一个完整的 RAG（检索增强生成）应用，用户上传文档后，系统自动解析、分块、向量化并存入 ChromaDB 向量数据库，随后即可通过 AI 对话界面基于文档内容进行智能问答，支持流式输出。

---

## 目录

- [技术架构](#技术架构)
- [项目目录结构](#项目目录结构)
- [开发环境搭建](#开发环境搭建)
- [后端详解](#后端详解)
  - [入口与生命周期](#入口与生命周期)
  - [核心配置](#核心配置)
  - [数据库层](#数据库层)
  - [数据模型](#数据模型)
  - [API 接口层](#api-接口层)
  - [服务层](#服务层)
  - [认证系统](#认证系统)
  - [日志与中间件](#日志与中间件)
- [前端详解](#前端详解)
  - [入口与全局配置](#入口与全局配置)
  - [路由系统](#路由系统)
  - [API 封装](#api-封装)
  - [页面组件](#页面组件)
- [RAG 工作流程](#rag-工作流程)
- [Docker 部署](#docker-部署)
- [CI/CD](#cicd)
- [测试](#测试)
- [环境变量说明](#环境变量说明)

---

## 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    浏览器 (Vue 3 SPA)                │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│  │ 首页 │ │ 上传 │ │ 聊天 │ │ 检索 │ │ 历史 │      │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘      │
│     └────────┴────────┴────────┴────────┘           │
│                    Axios / Fetch                      │
└────────────────────────┬────────────────────────────┘
                         │ HTTP / SSE
┌────────────────────────▼────────────────────────────┐
│              FastAPI 后端 (端口 8000)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ JWT 认证  │ │ 日志中间件│ │ CORS     │             │
│  └──────────┘ └──────────┘ └──────────┘             │
│  ┌──────────────────────────────────────┐            │
│  │           API 路由层                  │            │
│  │ /auth  /upload  /chat  /search ...  │            │
│  └──────────────┬───────────────────────┘            │
│  ┌──────────────▼───────────────────────┐            │
│  │           服务层                      │            │
│  │ RAGService → LLMService + Embedding  │            │
│  │             + VectorStore             │            │
│  └──────┬──────────┬──────────┬─────────┘            │
│         │          │          │                       │
│  ┌──────▼──┐ ┌─────▼────┐ ┌──▼──────────┐           │
│  │ SQLite  │ │ ChromaDB │ │ Ollama API  │           │
│  │ (关系库) │ │ (向量库) │ │ (大模型服务) │           │
│  └─────────┘ └──────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────┘
```

**核心技术选型：**

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | 组合式 API，开发体验好 |
| UI 组件库 | Element Plus | 企业级 Vue 3 组件库 |
| HTTP 客户端 | Axios | 请求拦截器自动带 JWT |
| 后端框架 | FastAPI | 异步高性能，自动生成 API 文档 |
| ORM | SQLAlchemy 2.0 | 声明式映射，类型安全 |
| 数据验证 | Pydantic v2 | 请求/响应模型校验 |
| 关系数据库 | SQLite | 轻量级，开发阶段无需额外安装 |
| 向量数据库 | ChromaDB | 轻量级本地向量存储 |
| 文本向量化 | BAAI/bge-small-zh-v1.5 | 中文语义向量模型 |
| 大语言模型 | Ollama (qwen2.5:3b) | 本地部署，数据不出本机 |
| 认证 | JWT (HS256) | 无状态令牌认证 |
| 流式输出 | SSE (Server-Sent Events) | 逐字输出，打字机效果 |
| 容器化 | Docker + docker-compose | 一键部署 |
| CI/CD | GitHub Actions | 自动测试与构建 |

---

## 项目目录结构

```
DocMind/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI 配置
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 应用入口
│   │   ├── api/                    # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # 认证接口（注册/登录/当前用户）
│   │   │   ├── chat.py             # 普通聊天接口
│   │   │   ├── chat_stream.py      # SSE 流式聊天接口
│   │   │   ├── documents.py        # 文档 CRUD 接口
│   │   │   ├── health.py           # 健康检查接口
│   │   │   ├── history.py          # 聊天历史接口
│   │   │   ├── search.py           # 知识检索接口
│   │   │   └── upload.py           # 文件上传接口
│   │   ├── core/                   # 核心配置与基础设施
│   │   │   ├── config.py           # 环境变量与全局配置
│   │   │   ├── database.py         # 数据库兼容层（重导出）
│   │   │   ├── logging.py          # 日志配置
│   │   │   ├── middleware.py       # 请求日志中间件
│   │   │   └── security.py         # JWT 令牌工具
│   │   ├── db/                     # 数据库初始化
│   │   │   ├── __init__.py
│   │   │   └── database.py         # SQLAlchemy 引擎与会话
│   │   ├── models/                 # ORM 数据模型
│   │   │   ├── base.py             # Base 重导出
│   │   │   ├── chat_history.py     # 聊天历史模型
│   │   │   ├── chunk.py            # 文档分块模型
│   │   │   ├── document.py         # 文档模型
│   │   │   └── user.py             # 用户模型
│   │   ├── schemas/                # Pydantic 请求/响应模型
│   │   │   ├── auth.py             # 认证相关模型
│   │   │   ├── chat.py             # 聊天相关模型
│   │   │   ├── document.py         # 文档相关模型
│   │   │   ├── health.py           # 健康检查模型
│   │   │   ├── history.py          # 历史记录模型
│   │   │   └── search.py           # 检索相关模型
│   │   └── services/               # 业务逻辑层
│   │       ├── __init__.py         # 服务单例工厂
│   │       ├── analysis_service.py # AI 分析服务
│   │       ├── docx_loader.py      # DOCX 文件解析
│   │       ├── embedding.py        # 文本向量化服务
│   │       ├── llm.py              # 大模型调用服务
│   │       ├── markdown_loader.py  # Markdown 文件解析
│   │       ├── pdf_loader.py       # PDF 文件解析
│   │       ├── prompt.py           # Prompt 模板管理
│   │       ├── rag_service.py      # RAG 核心服务
│   │       ├── splitter.py         # 文本分块服务
│   │       └── vector_store.py     # 向量存储服务
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py             # API 测试用例
│   ├── Dockerfile                  # 后端 Docker 镜像
│   └── requirements.txt            # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js            # Axios 封装与 API 方法
│   │   ├── router/
│   │   │   └── index.js            # Vue Router 路由配置
│   │   ├── views/
│   │   │   ├── ChatView.vue        # AI 聊天页面
│   │   │   ├── DocumentDetailView.vue  # 文档详情页面
│   │   │   ├── HistoryView.vue     # 历史记录页面
│   │   │   ├── HomeView.vue        # 首页
│   │   │   ├── LoginView.vue       # 登录/注册页面
│   │   │   ├── SearchView.vue      # 知识检索页面
│   │   │   └── UploadView.vue      # 文档上传页面
│   │   ├── App.vue                 # 根组件（导航栏 + 路由出口）
│   │   └── main.js                 # Vue 应用入口
│   ├── Dockerfile                  # 前端 Docker 镜像
│   ├── nginx.conf                  # Nginx 配置
│   ├── index.html                  # HTML 入口
│   ├── package.json                # 前端依赖
│   └── vite.config.js              # Vite 构建配置
├── .env.example                    # 环境变量示例
├── .gitignore                      # Git 忽略规则
├── docker-compose.yml              # Docker Compose 编排
└── README.md                       # 项目文档
```

---

## 开发环境搭建

### 前置条件

- Python 3.9+
- Node.js 20+
- [Ollama](https://ollama.ai) 已安装并运行
- 已拉取模型：`ollama pull qwen2.5:3b`

### 后端启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端启动（开发模式）

```bash
cd frontend
npm install
npm run dev
```

开发模式下 Vite 会自动将 `/api` 请求代理到 `http://localhost:8000`。

### 生产模式（前后端一体）

```bash
# 先构建前端
cd frontend
npm install
npm run build

# 将构建产物复制到后端的 static 目录
cp -r dist/* ../backend/static/

# 只启动后端，FastAPI 自动托管前端静态文件
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 即可使用完整应用。

---

## 后端详解

### 入口与生命周期

**文件：** `backend/app/main.py`

这是整个后端的入口文件，负责：

1. **创建 FastAPI 实例**，设置标题和版本号
2. **定义生命周期**（lifespan）：应用启动时初始化日志和数据库表
3. **注册中间件**：请求日志中间件 + CORS 跨域中间件
4. **注册路由**：所有 API 路由统一挂载到 `/api` 前缀下
5. **托管前端静态文件**：生产模式下 FastAPI 直接提供 Vue 构建产物

```python
@asynccontextmanager
async def lifespan(application: FastAPI):
    setup_logging()    # 初始化日志格式
    init_db()          # 创建数据库表
    yield

app = FastAPI(title="DocMind API", version="0.1.0", lifespan=lifespan)
```

静态文件托管逻辑：
- `/assets/*` → 映射到 `backend/static/assets/` 目录
- `/` → 返回 `index.html`
- `/{path}` → 如果文件存在就返回文件，否则返回 `index.html`（SPA 路由兜底）

### 核心配置

**文件：** `backend/app/core/config.py`

所有配置通过环境变量读取，支持 `.env` 文件：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `APP_NAME` | DocMind | 应用名称 |
| `APP_ENV` | development | 运行环境（development/production） |
| `APP_DEBUG` | true | 调试模式 |
| `BACKEND_HOST` | 0.0.0.0 | 监听地址 |
| `BACKEND_PORT` | 8000 | 监听端口 |
| `DATABASE_URL` | sqlite:///./docmind.db | 数据库连接字符串 |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama 服务地址 |
| `DEFAULT_MODEL` | qwen2.5:3b | 默认大模型名称 |
| `SECRET_KEY` | docmind-dev-secret-change-in-production | JWT 签名密钥 |
| `JWT_ALGORITHM` | HS256 | JWT 加密算法 |
| `JWT_EXPIRE_MINUTES` | 1440 | 令牌过期时间（分钟） |

加载逻辑：先通过 `dotenv` 加载项目根目录的 `.env` 文件，然后逐个用 `os.getenv()` 读取，提供合理的默认值。

### 数据库层

**文件：** `backend/app/db/database.py`

使用 SQLAlchemy 2.0 的声明式映射：

```python
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

- `engine`：数据库引擎，`check_same_thread=False` 是 SQLite 多线程必需参数
- `SessionLocal`：会话工厂，每个请求创建一个独立会话
- `Base`：所有 ORM 模型的基类
- `init_db()`：导入所有模型后调用 `Base.metadata.create_all()` 自动建表
- `get_db_session()`：FastAPI 依赖注入用的生成器，请求结束自动关闭会话

`backend/app/core/database.py` 是一个兼容层，仅重导出 `db/database.py` 的内容。

### 数据模型

#### Document — 文档模型

**文件：** `backend/app/models/document.py`

```python
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int]          # 主键，自增
    file_name: Mapped[str]   # 文件名（最长 255）
    file_type: Mapped[str]   # 文件类型（pdf/docx/md）
    file_path: Mapped[str]   # 服务器存储路径
    upload_time: Mapped[datetime]  # 上传时间（UTC）
```

#### DocumentChunk — 文档分块模型

**文件：** `backend/app/models/chunk.py`

```python
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int]              # 主键
    document_id: Mapped[int]     # 外键 → documents.id
    content: Mapped[str]         # 分块文本内容
    chunk_index: Mapped[int]     # 分块序号
    chunk_metadata: Mapped[dict] # JSON 元数据（页码、来源等）
```

通过 `document_id` 外键关联到 Document，实现一对多关系。`chunk_metadata` 使用 JSON 列存储灵活的元数据。

#### ChatHistory — 聊天历史模型

**文件：** `backend/app/models/chat_history.py`

```python
class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id: Mapped[int]           # 主键
    question: Mapped[str]     # 用户问题
    answer: Mapped[str]       # AI 回答
    create_time: Mapped[datetime]  # 创建时间
```

每次对话完成后自动保存，供历史记录页面展示。

#### User — 用户模型

**文件：** `backend/app/models/user.py`

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int]              # 主键
    username: Mapped[str]        # 用户名（唯一，有索引）
    hashed_password: Mapped[str] # 密码哈希值
```

密码使用 PBKDF2-HMAC-SHA256 算法哈希，迭代 100000 次：
- `hash_password()`：生成随机 16 字节盐，计算哈希，格式为 `salt:hash`
- `verify_password()`：提取盐值重新计算哈希，用 `hmac.compare_digest` 做时间安全的比较

### API 接口层

所有 API 路由统一挂载到 `/api` 前缀下。

#### 健康检查 — `health.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 返回服务状态 |

响应示例：`{"status": "ok", "app": "DocMind"}`

用于部署监控和负载均衡器健康探测。

#### 认证 — `auth.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/token` | 用户登录（OAuth2 兼容） |
| GET | `/api/auth/me` | 获取当前用户信息 |

**注册流程：**
1. 接收 `username` + `password`
2. 检查用户名是否已存在
3. 调用 `User.hash_password()` 哈希密码
4. 写入数据库，返回用户信息

**登录流程：**
1. 接收 OAuth2 表单格式的用户名密码
2. 查询用户，验证密码
3. 调用 `create_access_token()` 生成 JWT
4. 返回 `{"access_token": "...", "token_type": "bearer"}`

**认证依赖 `require_auth`：**
- 从请求头提取 Bearer Token
- 解码 JWT 获取 `sub`（用户名）
- 查询数据库验证用户存在
- 返回 User 对象供后续接口使用

#### 文件上传 — `upload.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传文档文件 |

**完整上传流程：**

```
用户上传文件
    │
    ▼
校验文件名和类型（仅允许 .pdf/.docx/.md/.markdown）
    │
    ▼
安全化文件名（移除特殊字符）+ 重名处理
    │
    ▼
分块写入服务器（每 1MB 一块，超过 100MB 拒绝）
    │
    ▼
写入 Document 记录到数据库
    │
    ▼
根据文件类型选择对应的 Loader 解析内容
    │
    ▼
SplitterService 将文本切分为 ~500 字的分块（重叠 100 字）
    │
    ▼
EmbeddingService 将每个分块转为 384 维向量
    │
    ▼
VectorStore 将向量 + 元数据存入 ChromaDB
    │
    ▼
将 DocumentChunk 记录写入数据库
    │
    ▼
返回 {"success": true, "document_id": 1, "filename": "xxx.pdf"}
```

关键安全措施：
- `_sanitize_filename()`：移除路径穿越字符
- `_allowed_file()`：白名单校验文件扩展名
- `_save_upload_file()`：流式写入 + 大小限制，防止内存溢出

#### 文档管理 — `documents.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/documents` | 文档列表（分页） |
| GET | `/api/documents/{id}` | 文档详情（含分块） |
| DELETE | `/api/documents/{id}` | 删除文档 |

删除文档时会：
1. 删除服务器上的物理文件
2. 删除数据库中的 DocumentChunk 记录
3. 从 ChromaDB 向量库中删除对应向量

#### 聊天 — `chat.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 普通聊天（等待完整回答） |

接收问题 → 调用 RAG 服务 → 保存聊天历史 → 返回回答

#### 流式聊天 — `chat_stream.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/stream` | SSE 流式聊天 |

这是核心的聊天接口，使用 Server-Sent Events 实现逐字输出：

```python
def event_generator():
    full_answer = ""
    for chunk in rag.answer_stream(request.question):
        full_answer += chunk
        data = json.dumps({"content": chunk}, ensure_ascii=False)
        yield f"data: {data}\n\n"    # SSE 格式
    yield "data: [DONE]\n\n"         # 结束标记
    # 流结束后保存完整回答到数据库
```

返回 `StreamingResponse`，设置 `text/event-stream` 媒体类型和 `X-Accel-Buffering: no`（禁用 Nginx 缓冲）。

#### 知识检索 — `search.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/search` | 知识检索（返回回答 + 来源） |

与聊天接口类似，但额外返回 `sources` 字段，包含匹配的文档片段和距离分数。

#### 历史记录 — `history.py`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/history` | 聊天历史列表（分页） |

按创建时间倒序排列，支持 `skip` 和 `limit` 分页参数。

### 服务层

服务层是项目的核心业务逻辑，采用**单例模式**（通过 `__init__.py` 的工厂函数）避免重复初始化。

#### 服务工厂 — `services/__init__.py`

```python
_vector_store = None
_embedding_service = None
_llm_service = None
_rag_service = None

def get_vector_store():    # 懒加载 VectorStore
def get_embedding_service():  # 懒加载 EmbeddingService
def get_llm_service():     # 懒加载 LLMService
def get_rag_service():     # 组装 RAGService
```

所有服务在首次调用时初始化，后续复用同一实例。初始化失败时返回 `None` 而非抛异常，保证服务降级可用。

#### LLMService — 大模型服务

**文件：** `backend/app/services/llm.py`

封装 Ollama Python SDK，提供三种调用方式：

| 方法 | 说明 | 使用场景 |
|------|------|---------|
| `generate(prompt)` | 同步生成，返回完整文本 | 普通聊天、分析 |
| `generate_stream(prompt)` | 流式生成，逐块 yield 文本 | SSE 流式聊天 |
| `chat(messages)` | 多轮对话模式 | 预留的多轮对话 |

```python
class LLMService:
    def __init__(self, model_name=None, base_url=None):
        self.client = Client(host=base_url or OLLAMA_BASE_URL)
        self.model_name = model_name or DEFAULT_MODEL
```

#### EmbeddingService — 向量化服务

**文件：** `backend/app/services/embedding.py`

使用 `sentence-transformers` 加载 `BAAI/bge-small-zh-v1.5` 中文向量模型：

| 方法 | 说明 |
|------|------|
| `embed_chunks(chunks)` | 批量将文本块转为向量，返回带 embedding 字段的列表 |
| `embed_query(text)` | 将用户查询转为向量，用于相似度搜索 |

模型输出 384 维向量，适合中文语义检索。

#### VectorStore — 向量存储服务

**文件：** `backend/app/services/vector_store.py`

封装 ChromaDB 的增删查操作：

| 方法 | 说明 |
|------|------|
| `add_documents(documents)` | 批量添加向量文档 |
| `delete_documents(ids)` | 按 ID 删除向量 |
| `query_top_k(query_embedding, top_k)` | 查询最相似的 top_k 个文档 |

使用 `chromadb.PersistentClient` 持久化存储到 `backend/chromadb/` 目录。

#### RAGService — RAG 核心服务

**文件：** `backend/app/services/rag_service.py`

这是整个项目的核心，组合了向量检索和大模型生成：

```python
class RAGService:
    def __init__(self, vector_store, llm_service, embedding_service):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.embedding_service = embedding_service
```

**`answer(question)` 方法流程：**
1. 将问题向量化：`embedding_service.embed_query(question)`
2. 在向量库中检索最相似的 5 个文档块：`vector_store.query_top_k()`
3. 将检索结果拼接为上下文
4. 构建 Prompt：`请基于以下内容回答问题，并给出引用来源。\n\n{context}\n\n问题：{question}\n\n回答：`
5. 调用大模型生成回答：`llm_service.generate(prompt)`
6. 返回回答和来源

**`answer_stream(question)` 方法：** 与 `answer()` 相同的检索逻辑，但使用 `llm_service.generate_stream()` 逐块输出。

#### SplitterService — 文本分块服务

**文件：** `backend/app/services/splitter.py`

采用滑动窗口算法将长文本切分为固定大小的块：

- `chunk_size`：每块最大 500 字符
- `chunk_overlap`：块之间重叠 100 字符（保证上下文连贯）
- 优先在空格处断句，避免截断单词

```python
while start < text_length:
    end = min(start + self.chunk_size, text_length)
    chunk = text[start:end]
    # 尝试在空格处断句
    if end < text_length:
        last_space = chunk.rfind(" ")
        if last_space > max(self.chunk_size // 2, 20):
            end = start + last_space
    chunks.append(chunk.strip())
    start = max(end - self.chunk_overlap, end)
```

#### 文档解析器

三个 Loader 负责将不同格式的文件解析为统一的 `[{text, metadata}]` 结构：

| Loader | 文件 | 输出格式 |
|--------|------|---------|
| `PDFLoaderService` | `pdf_loader.py` | `{text, page, source}` — 按页提取 |
| `DOCXLoaderService` | `docx_loader.py` | `{text, paragraph, source}` — 按段落提取 |
| `MarkdownLoaderService` | `markdown_loader.py` | `{text, source}` — 清洗标签后提取 |

PDF 使用 PyMuPDF (fitz) 库，DOCX 使用 python-docx 库，Markdown 使用正则表达式清洗格式标签。

#### AnalysisService — AI 分析服务

**文件：** `backend/app/services/analysis_service.py`

封装了四种 AI 文本分析能力：

| 方法 | 说明 | Prompt 模板 |
|------|------|-------------|
| `summarize(context)` | 生成摘要 | SUMMARY_PROMPT |
| `keywords(context)` | 提取关键词 | KEYWORDS_PROMPT |
| `knowledge_points(context)` | 提取知识点 | KNOWLEDGE_POINTS_PROMPT |
| `chapter_summary(context)` | 章节总结 | CHAPTER_SUMMARY_PROMPT |

#### Prompt 模板 — `prompt.py`

```python
SUMMARY_PROMPT = "请阅读以下内容并给出简洁的摘要：\n\n{context}\n\n摘要："
KEYWORDS_PROMPT = "请从以下内容中提取关键词，返回关键词列表：\n\n{context}\n\n关键词："
KNOWLEDGE_POINTS_PROMPT = "请从以下内容中提取知识点，并按照要点形式输出：\n\n{context}\n\n知识点："
CHAPTER_SUMMARY_PROMPT = "请基于以下章节内容生成章节总结：\n\n{context}\n\n章节总结："
```

### 认证系统

**文件：** `backend/app/core/security.py`

JWT 令牌的创建与验证：

```python
def create_access_token(data: dict, expires_delta=None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

- 使用 `python-jose` 库实现 JWT 编解码
- 令牌载荷包含 `sub`（用户名）和 `exp`（过期时间）
- 默认有效期 1440 分钟（24 小时）

### 日志与中间件

#### 日志配置 — `logging.py`

```python
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
```

- 开发环境：DEBUG 级别
- 生产环境：INFO 级别
- 输出到 stdout，方便容器日志收集
- 清除 uvicorn 默认 handler 避免重复输出

#### 请求日志中间件 — `middleware.py`

每个请求自动记录：

```
2026-07-14 18:32:24 | INFO     | access | POST /api/chat/stream 200 1523.4ms request_id=a1b2c3d4
```

- 自动生成 `X-Request-ID`（8 位随机十六进制）
- 计算响应时间并写入 `X-Response-Time` 响应头
- 方便排查问题和性能分析

---

## 前端详解

### 入口与全局配置

**文件：** `frontend/src/main.js`

```javascript
const app = createApp(App)
app.use(createPinia())    // 状态管理
app.use(ElementPlus)      // UI 组件库
app.use(router)           // 路由
app.mount('#app')
```

### 路由系统

**文件：** `frontend/src/router/index.js`

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | HomeView | 首页 |
| `/login` | LoginView | 登录/注册（`meta.guest: true`） |
| `/upload` | UploadView | 上传文档 |
| `/documents/:id` | DocumentDetailView | 文档详情 |
| `/chat` | ChatView | AI 聊天 |
| `/search` | SearchView | 知识检索 |
| `/history` | HistoryView | 历史记录 |

**导航守卫：**

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.guest && !token) {
    next({ name: 'login' })     // 未登录 → 跳转登录页
  } else if (to.meta.guest && token) {
    next({ name: 'home' })      // 已登录 → 跳转首页
  } else {
    next()
  }
})
```

### API 封装

**文件：** `frontend/src/api/index.js`

基于 Axios 封装，统一管理所有 API 调用：

**请求拦截器：** 自动在请求头添加 `Authorization: Bearer <token>`

**响应拦截器：** 收到 401 响应时自动清除 token 并跳转登录页

**导出的 API 方法：**

| 方法 | 说明 |
|------|------|
| `registerUser(username, password)` | 用户注册 |
| `login(username, password)` | 用户登录 |
| `getMe()` | 获取当前用户 |
| `listDocuments(skip, limit)` | 文档列表 |
| `getDocument(id)` | 文档详情 |
| `deleteDocument(id)` | 删除文档 |
| `uploadDocument(file)` | 上传文档 |
| `chatQuestion(question)` | 普通聊天 |
| `chatStreamUrl()` | 获取流式聊天 URL |
| `searchQuestion(question)` | 知识检索 |
| `listHistory(skip, limit)` | 历史记录 |
| `healthCheck()` | 健康检查 |

### 页面组件

#### App.vue — 根组件

顶部导航栏 + 路由出口，包含：
- 品牌 Logo（点击回首页）
- 5 个导航链接（首页/上传/聊天/检索/历史）
- 退出登录按钮（仅登录后显示）
- 页面切换过渡动画（`page-fade`）

#### HomeView.vue — 首页

- **Hero 区域**：带粒子动画的标题和行动按钮
- **统计卡片**：实时显示文档数、问答数、服务状态
- **功能卡片**：6 个功能入口，hover 时图标弹跳动画

#### LoginView.vue — 登录/注册

- 登录和注册共用一个组件，通过 `isRegister` 切换
- 登录成功后将 JWT 存入 `localStorage`
- 使用 Element Plus 的表单组件和消息提示

#### ChatView.vue — AI 聊天（核心页面）

这是最复杂的前端组件，实现了 SSE 流式接收：

```javascript
const response = await fetch(chatStreamUrl(), {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({ question: q }),
})

const reader = response.body.getReader()
const decoder = new TextDecoder()
let buffer = ''

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  buffer += decoder.decode(value, { stream: true })
  const lines = buffer.split('\n')
  buffer = lines.pop() || ''

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || !trimmed.startsWith('data: ')) continue
    const data = trimmed.slice(6)
    if (data === '[DONE]') continue
    const parsed = JSON.parse(data)
    if (parsed.content) {
      reactiveMsg.content += parsed.content  // 逐字追加
    }
  }
}
```

为什么用 `fetch` 而不是 `axios`？因为 Axios 不原生支持 ReadableStream，而 `fetch` 的 `response.body.getReader()` 可以逐块读取 SSE 数据流。

特性：
- 打字机效果（逐字追加 + 闪烁光标）
- 思考中动画（三个跳动的点）
- 推荐问题标签（点击直接填入输入框）
- 消息列表平滑滚动

#### UploadView.vue — 文档上传

- 拖拽上传区域（支持 drag & drop）
- 文件类型图标自动匹配（📕PDF / 📘DOCX / 📝MD）
- 上传进度条
- 上传成功结果卡片
- 最近上传文件列表

#### SearchView.vue — 知识检索

- 搜索输入框
- AI 回答卡片
- 参考来源列表（可展开/折叠查看原文）
- 距离分数显示

#### HistoryView.vue — 历史记录

- 问答记录列表（Q/A 标签区分）
- 加载更多分页
- "重新提问"按钮（跳转到聊天页并带入问题）

#### DocumentDetailView.vue — 文档详情

- 文档元信息（文件名、类型、上传时间、分块数）
- 分块内容网格（可展开/折叠长文本）

---

## RAG 工作流程

RAG（Retrieval-Augmented Generation，检索增强生成）是本项目的核心架构：

```
用户提问："这个文档的核心结论是什么？"
         │
         ▼
┌─────────────────────┐
│ 1. 问题向量化         │  EmbeddingService.embed_query()
│    问题 → 384维向量   │  使用 bge-small-zh-v1.5 模型
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. 向量相似度检索     │  VectorStore.query_top_k()
│    在 ChromaDB 中     │  返回最相似的 5 个文档块
│    找到最相关的段落   │  按余弦距离排序
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. 构建 Prompt        │  RAGService
│    检索结果 + 问题    │  "请基于以下内容回答问题..."
│    → 完整提示词       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 4. 大模型生成回答     │  LLMService.generate()
│    Ollama qwen2.5:3b │  或 generate_stream() 流式输出
│    基于上下文回答     │
└─────────┬───────────┘
          │
          ▼
     AI 回答 + 引用来源
```

**为什么用 RAG 而不是直接让大模型回答？**

1. **准确性**：大模型可能"幻觉"（编造答案），RAG 限定回答范围在文档内容内
2. **实时性**：文档更新后无需重新训练模型，只需更新向量库
3. **可追溯**：每个回答都有引用来源，用户可以验证
4. **隐私性**：文档数据保留在本地，不需要上传到云端 API

---

## Docker 部署

### docker-compose.yml

```yaml
services:
  backend:                    # 后端服务
    build: ./backend
    ports: ["8000:8000"]
    volumes: [backend-data:/app/data]  # 数据持久化
    environment:
      - DATABASE_URL=sqlite:///data/docmind.db
      - OLLAMA_BASE_URL=http://host.docker.internal:11434  # 访问宿主机 Ollama
      - SECRET_KEY=change-this-in-production  # 生产环境务必修改！
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Docker 访问宿主机

  frontend:                   # 前端服务
    build: ./frontend
    ports: ["80:80"]
    depends_on: [backend]

volumes:
  backend-data:               # 命名卷，持久化数据库和向量
```

### 后端 Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端 Dockerfile（多阶段构建）

```dockerfile
FROM node:20-slim AS builder  # 第一阶段：构建
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine             # 第二阶段：部署
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Nginx 配置

```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;  # API 请求转发到后端
    proxy_buffering off;                   # 禁用缓冲，支持 SSE
    proxy_read_timeout 300s;              # 长超时，支持流式输出
}

location / {
    try_files $uri $uri/ /index.html;     # SPA 路由兜底
}
```

### 启动命令

```bash
docker-compose up --build -d
```

---

## CI/CD

**文件：** `.github/workflows/ci.yml`

每次推送到 `main` 分支或创建 PR 时自动运行：

**后端任务：**
1. Checkout 代码
2. 安装 Python 3.11
3. `pip install -r requirements.txt`
4. `python -m pytest tests/ -v`

**前端任务：**
1. Checkout 代码
2. 安装 Node 20
3. `npm install`
4. `npm run build`（验证构建成功）

---

## 测试

**文件：** `backend/tests/test_api.py`

使用 FastAPI 的 `TestClient` 进行集成测试，共 10 个用例：

| 测试 | 说明 |
|------|------|
| `test_health_check` | 健康检查返回 200 |
| `test_register_and_login` | 注册后能登录获取 token |
| `test_register_duplicate` | 重复注册返回 400 |
| `test_login_wrong_password` | 错误密码返回 401 |
| `test_me_with_token` | 带 token 获取用户信息成功 |
| `test_me_without_token` | 不带 token 返回 401 |
| `test_list_documents` | 文档列表接口正常 |
| `test_list_history` | 历史记录接口正常 |
| `test_chat_empty_question` | 空问题返回 400 |
| `test_search_empty_question` | 空检索返回 400 |

运行测试：

```bash
cd backend
python -m pytest tests/ -v
```

---

## 环境变量说明

**`.env.example`** 是环境变量模板，实际使用时复制为 `.env`：

```bash
cp .env.example .env
```

| 变量 | 示例值 | 必填 | 说明 |
|------|--------|------|------|
| `APP_NAME` | DocMind | 否 | 应用名称 |
| `APP_ENV` | development | 否 | 环境：development / production |
| `APP_DEBUG` | true | 否 | 调试模式开关 |
| `BACKEND_HOST` | 0.0.0.0 | 否 | 监听地址 |
| `BACKEND_PORT` | 8000 | 否 | 监听端口 |
| `DATABASE_URL` | sqlite:///./docmind.db | 否 | 数据库连接 |
| `OLLAMA_BASE_URL` | http://localhost:11434 | 否 | Ollama 地址 |
| `DEFAULT_MODEL` | qwen2.5:3b | 否 | 模型名称 |
| `SECRET_KEY` | change-this-in-production | **是** | JWT 密钥，生产环境必须修改！ |
| `JWT_ALGORITHM` | HS256 | 否 | JWT 算法 |
| `JWT_EXPIRE_MINUTES` | 1440 | 否 | Token 有效期（分钟） |

> ⚠️ `.env` 文件已在 `.gitignore` 中，不会被提交到 Git。`SECRET_KEY` 在生产环境中务必使用强随机字符串。