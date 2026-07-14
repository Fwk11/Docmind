"""
日志配置模块
============
统一管理应用的日志格式和输出。

日志有什么用？
- 开发时：帮你看到程序运行到哪一步了，出了什么问题
- 生产时：记录用户操作和系统错误，方便排查线上问题

日志格式示例：
2026-07-14 18:32:24 | INFO     | access | POST /api/chat/stream 200 1523.4ms request_id=a1b2c3d4
│                        │         │       │
│                        │         │       └── 日志消息
│                        │         └── 记录器名称（哪个模块打的日志）
│                        └── 日志级别（DEBUG/INFO/WARNING/ERROR）
└── 时间戳
"""

import logging
import sys
from app.core.config import APP_ENV

# 日志格式：时间 | 级别(8字符宽) | 记录器名 | 消息
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """
    初始化日志系统

    根据运行环境设置日志级别：
    - development：DEBUG 级别，输出所有日志（包括调试信息）
    - production：INFO 级别，只输出重要日志
    """
    level = logging.DEBUG if APP_ENV == "development" else logging.INFO

    # 创建控制台输出处理器，日志输出到标准输出（终端）
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # force=True 强制重新配置，覆盖已有的日志配置
    logging.basicConfig(level=level, handlers=[handler], force=True)

    # 清理 Uvicorn 自带的日志处理器，避免重复输出
    # Uvicorn 默认有自己的日志配置，如果不清理，同一条日志会输出两次
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    参数：
        name: 记录器名称，通常用模块名（如 "access"、"chat"）

    使用示例：
        logger = get_logger("chat")
        logger.info("用户发送了问题: %s", question)
    """
    return logging.getLogger(name)