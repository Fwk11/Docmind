"""
配置管理模块
============
这个文件负责从环境变量中读取所有配置项。

为什么要把配置放在环境变量里？
- 不同环境（开发/测试/生产）的配置不同，硬编码在代码里不方便切换
- 敏感信息（如密钥）不应该写在代码里，应该放在 .env 文件中
- .env 文件被 .gitignore 排除，不会提交到 GitHub，保护隐私

使用方式：
1. 复制 .env.example 为 .env
2. 在 .env 中填写实际配置
3. 本模块自动读取 .env 中的值，没有则使用默认值
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# 项目根目录：backend/ 的上一级，即 DocMind/
BASE_DIR = Path(__file__).resolve().parents[2]

# 加载 .env 文件中的环境变量
# load_dotenv 会把 .env 文件里的键值对注入到 os.environ 中
# 这样 os.getenv() 就能读到 .env 里定义的值了
load_dotenv(BASE_DIR / ".env")

# ============================================================
# 应用基本配置
# ============================================================
APP_NAME = os.getenv("APP_NAME", "DocMind")                          # 应用名称
APP_ENV = os.getenv("APP_ENV", "development")                       # 运行环境：development 或 production
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"        # 是否开启调试模式
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")                 # 后端监听地址，0.0.0.0 表示所有网卡
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))               # 后端监听端口

# ============================================================
# 数据库配置
# ============================================================
# SQLite 是轻量级数据库，数据存在单个文件中，不需要额外安装数据库服务
# sqlite:///./docmind.db 表示在当前目录下创建 docmind.db 文件
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'docmind.db'}")

# ============================================================
# Ollama 大模型配置
# ============================================================
# Ollama 是本地大模型服务，默认跑在 11434 端口
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# 默认使用 qwen2.5:3b 模型（通义千问 2.5 的 3B 参数版本，体积小、速度快）
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5:3b")

# ============================================================
# JWT 认证配置
# ============================================================
# JWT（JSON Web Token）是一种无状态的认证方案
# SECRET_KEY 是签名密钥，生产环境必须改成随机字符串！
# JWT_ALGORITHM 是签名算法，HS256 是最常用的对称加密算法
# JWT_EXPIRE_MINUTES 是令牌过期时间，默认 1440 分钟 = 24 小时
SECRET_KEY = os.getenv("SECRET_KEY", "docmind-dev-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))