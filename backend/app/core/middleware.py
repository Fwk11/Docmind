"""
请求日志中间件
==============
自动记录每个 HTTP 请求的详细信息。

中间件是什么？就像地铁站的安检：
- 每个请求进来都要先过中间件
- 中间件可以在请求处理前、后做额外操作
- 这个中间件专门记录请求日志

记录内容：
- HTTP 方法（GET/POST/PUT/DELETE）
- 请求路径（/api/chat/stream）
- 响应状态码（200/404/500）
- 处理耗时（毫秒）
- 请求 ID（用于追踪同一次请求的所有日志）

日志示例：
POST /api/chat/stream 200 1523.4ms request_id=a1b2c3d4
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import get_logger

logger = get_logger("access")


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    继承自 Starlette 的 BaseHTTPMiddleware，只需要实现 dispatch 方法。
    dispatch 方法在每次请求时被调用，参数：
    - request: 本次请求对象
    - call_next: 调用下一个中间件或路由处理函数的回调
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 生成请求 ID：优先使用客户端传来的 X-Request-ID，没有则随机生成
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:8])

        # 记录开始时间
        start = time.perf_counter()

        # 调用下一个处理函数，获取响应
        response = await call_next(request)

        # 计算耗时（毫秒）
        elapsed = (time.perf_counter() - start) * 1000

        # 输出访问日志
        logger.info(
            "%s %s %s %.1fms request_id=%s",
            request.method,        # 请求方法：GET、POST 等
            request.url.path,      # 请求路径：/api/chat/stream
            response.status_code,  # 状态码：200、404 等
            elapsed,               # 耗时：1523.4
            request_id,            # 请求 ID：a1b2c3d4
        )

        # 在响应头中附加请求 ID 和耗时，方便前端调试
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed:.1f}ms"

        return response