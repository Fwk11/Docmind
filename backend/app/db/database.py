"""
数据库初始化模块
===============
负责创建数据库连接和初始化表结构。

SQLAlchemy 是什么？
- Python 最流行的 ORM（对象关系映射）库
- 让你用 Python 类来操作数据库，不用写 SQL 语句
- 例如：db.query(User).filter(User.username == "admin").first()
  等价于：SELECT * FROM users WHERE username = 'admin' LIMIT 1

这个文件做了三件事：
1. 创建数据库引擎（连接数据库）
2. 创建会话工厂（每次请求创建一个数据库会话）
3. 定义 Base 类（所有数据模型的基类）
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DATABASE_URL

# ============================================================
# 创建数据库引擎
# ============================================================
# 引擎是 SQLAlchemy 与数据库的"桥梁"，负责管理连接池
# connect_args={"check_same_thread": False} 是 SQLite 专用配置：
#   SQLite 默认只允许创建连接的线程使用它，
#   但 FastAPI 是多线程的，所以需要关闭这个限制
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ============================================================
# 创建会话工厂
# ============================================================
# SessionLocal 是一个工厂函数，调用它就能获得一个数据库会话
# autocommit=False: 不自动提交，需要手动 db.commit()
# autoflush=False: 不自动刷新，避免不必要的 SQL 执行
# bind=engine: 绑定到上面创建的引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================
# 定义模型基类
# ============================================================
# 所有数据模型（User、Document 等）都继承这个 Base 类
# Base.metadata.create_all() 会根据所有继承 Base 的模型类自动创建表
class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """
    初始化数据库：根据模型定义创建所有表

    这个函数在应用启动时被调用（main.py 的 lifespan 中）
    如果表已存在，不会重复创建
    如果表不存在，会根据模型定义自动创建

    注意：必须先导入所有模型类，SQLAlchemy 才能知道有哪些表要创建
    """
    # 导入所有模型，让 SQLAlchemy 注册它们的表定义
    from app.models.document import Document  # noqa: F401
    from app.models.chunk import DocumentChunk  # noqa: F401
    from app.models.chat_history import ChatHistory  # noqa: F401
    from app.models.user import User  # noqa: F401

    # 根据所有模型类创建数据库表
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """
    获取数据库会话的依赖注入函数

    这是 FastAPI 的依赖注入模式：
    - 在路由函数参数中写 db: Session = Depends(get_db_session)
    - FastAPI 会自动调用这个函数，把数据库会话传进来
    - 请求结束后自动关闭会话（finally 中的 db.close()）

    为什么用 yield 而不是 return？
    - yield 让函数变成生成器，请求处理完后会继续执行 finally 中的清理代码
    - 如果用 return，finally 中的 db.close() 会在请求处理前就执行了
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()