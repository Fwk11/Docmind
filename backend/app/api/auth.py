"""
认证 API 接口 — 提供注册、登录、获取用户信息三个接口

认证流程：
1. 用户注册 → 创建账号（密码哈希后存储）
2. 用户登录 → 验证密码 → 生成 JWT 令牌 → 返回给前端
3. 访问受保护接口 → 前端带 JWT 令牌 → 后端验证 → 返回数据

依赖注入（Depends）是什么？
- FastAPI 的核心特性，自动给路由函数传参
- 例如 require_auth 写在参数里，FastAPI 会自动执行认证逻辑
- 不用在每个路由函数里重复写认证代码
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token
from app.db.database import get_db_session
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRegister, UserOut

router = APIRouter()

# HTTPBearer：自动从请求头提取 Bearer 令牌的认证方案
from fastapi import Request as _Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_bearer = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db_session),
) -> User:
    """认证依赖：提取令牌→解码→查用户，任何一步失败返回401"""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭据")
    payload = decode_access_token(credentials.credentials)  # 解码JWT
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或过期的令牌")
    username = payload.get("sub")  # 从令牌中取用户名
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")
    user = db.query(User).filter(User.username == username).first()  # 查数据库
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


@router.post("/auth/register", response_model=UserOut)
def register(body: UserRegister, db: Session = Depends(get_db_session)):
    """注册：检查重名→哈希密码→存数据库→返回用户信息(不含密码)"""
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=body.username, hashed_password=User.hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/token", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    """登录：查用户→验密码→发JWT令牌。用OAuth2PasswordRequestForm符合OAuth2标准"""
    user = db.query(User).filter(User.username == form.username).first()
    if user is None or not user.verify_password(form.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username})  # sub存用户名
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(require_auth)):
    """获取当前用户信息，require_auth自动验证令牌"""
    return current_user