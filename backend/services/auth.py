import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from models.auth_models import User
from models.api_model import Token
from .security import SECRET_KEY, ALGORITHM, password_hash, DUMMY_HASH, ACCESS_TOKEN_EXPIRE_MINUTES
from database.database import get_db
from database.user_repository import get_user

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    JWT アクセストークンを生成する。

    Args:
        data: トークンへ埋め込むペイロード。
        expires_delta: 有効期限。None の場合は無期限。

    Returns:
        JWT アクセストークン。
    """
    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:
    """
    ユーザー名とパスワードを認証する。

    Args:
        db: データベースセッション。
        username: ユーザー名。
        password: 平文パスワード。

    Returns:
        User: 認証成功時。
        None: 認証失敗時。
    """
    user = get_user(db, username)

    if user is None:
        password_hash.verify(password, DUMMY_HASH)
        return None

    if not password_hash.verify(password, user.hashed_password):
        return None

    return user


def login(
    db: Session,
    form_data: OAuth2PasswordRequestForm,
) -> Token:
    """
    ログインを行いアクセストークンを発行する。

    Args:
        db: データベースセッション。
        form_data: ログインフォーム。

    Returns:
        発行したアクセストークン。

    Raises:
        HTTPException: ユーザー名またはパスワードが不正な場合。
    """
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if user is None:
        logger.warning("Login failed: username=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        logger.info("Login succeeded: username=%s", user.username)

    if ACCESS_TOKEN_EXPIRE_MINUTES is None:
        access_token = create_access_token(
            data={"sub": user.username},
        )
    else:
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    JWT を検証し、ログイン中のユーザーを取得する。

    Args:
        token: Bearer トークン。
        db: データベースセッション。

    Returns:
        認証済みユーザー。

    Raises:
        HTTPException: トークンが不正またはユーザーが存在しない場合。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username = payload.get("sub")
        if not isinstance(username, str):
            logger.warning("Invalid authentication token: missing subject")
            raise credentials_exception

    except ExpiredSignatureError as exc:
        logger.warning("Authentication token expired")
        raise credentials_exception from exc

    except InvalidTokenError as exc:
        logger.warning("Invalid authentication token")
        raise credentials_exception from exc

    user = get_user(db, username)

    if user is None:
        raise credentials_exception

    return user
