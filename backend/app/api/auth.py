from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token
from app.db.database import get_db_session
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRegister, UserOut
from app.core.config import SECRET_KEY, JWT_ALGORITHM

router = APIRouter()


def get_current_user(token: str = None, db: Session = Depends(get_db_session)) -> User:
    from fastapi import Request
    raise HTTPException(status_code=501, detail="Use dependency injection version")


from fastapi import Request as _Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_bearer = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭据")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或过期的令牌")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


@router.post("/auth/register", response_model=UserOut)
def register(body: UserRegister, db: Session = Depends(get_db_session)):
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
    user = db.query(User).filter(User.username == form.username).first()
    if user is None or not user.verify_password(form.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(require_auth)):
    return current_user