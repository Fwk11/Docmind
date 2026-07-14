"""
JWT 安全模块
============
负责生成和验证 JWT 令牌（JSON Web Token）。

JWT 是什么？就像一张加密的身份证：
- 里面存着用户信息（如用户名）和过期时间
- 任何人都可以读取内容，但无法篡改（因为需要密钥签名）
- 前端每次请求都带上这个令牌，后端验证后就知道你是谁了

工作流程：
1. 用户登录 → 后端生成 JWT 令牌 → 返回给前端
2. 前端把令牌存到 localStorage
3. 之后每次请求都在 Header 里带上：Authorization: Bearer <令牌>
4. 后端验证令牌 → 解析出用户名 → 查询用户 → 处理请求
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT 令牌

    参数：
        data: 要存入令牌的数据，通常是 {"sub": "用户名"}
        expires_delta: 自定义过期时间间隔，不传则使用默认值

    返回：
        编码后的 JWT 字符串

    令牌内容示例（解码后）：
        {"sub": "admin", "exp": 1721000000}
        - sub: subject，即用户名
        - exp: expiration，过期时间的时间戳
    """
    to_encode = data.copy()
    # 计算过期时间：当前时间 + 过期间隔
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    # 使用密钥和算法编码为 JWT 字符串
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    验证并解码 JWT 令牌

    参数：
        token: JWT 字符串

    返回：
        解码后的字典（包含 sub、exp 等），验证失败返回 None

    验证失败的情况：
    - 令牌被篡改（签名不匹配）
    - 令牌已过期（exp 时间已过）
    - 令牌格式不正确
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        # 任何解码错误都返回 None，不暴露具体原因（安全考虑）
        return None