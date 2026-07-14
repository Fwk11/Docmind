"""
认证相关的数据校验模型
======================
定义注册、登录、获取用户信息时 API 的输入输出格式。

Pydantic 是什么？
- FastAPI 用来校验数据的工具
- 你定义一个类，声明每个字段的类型
- FastAPI 自动帮你校验请求参数，类型不对就返回 422 错误
- 还能自动生成 API 文档

为什么需要 from_attributes=True？
- 因为 API 返回的是 SQLAlchemy 模型对象（如 User 实例）
- Pydantic 默认只能从字典读取数据
- from_attributes=True 让 Pydantic 也能从对象属性读取数据
"""

from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    """注册请求模型：用户需要提供用户名和密码"""
    username: str
    password: str


class UserOut(BaseModel):
    """用户信息响应模型：返回给前端的用户数据（不包含密码！）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class TokenResponse(BaseModel):
    """登录响应模型：返回 JWT 令牌"""
    access_token: str          # JWT 令牌字符串
    token_type: str = "bearer" # 令牌类型，固定为 "bearer"