from sqlalchemy.orm import Session
from models.auth_models import User


def get_user(
    db: Session,
    username: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def create_user(
    db: Session,
    username: str,
    is_admin: bool,
    hashed_password: str,
) -> User:
    """
    ユーザーを作成する。

    Args:
        db: DBセッション
        username: ユーザー名
        hashed_password: ハッシュ化済みパスワード
        disabled: 無効フラグ

    Returns:
        作成されたUser
    """

    user = User(
        username=username,
        is_admin=is_admin,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    username: str,
) -> bool:
    """
    ユーザーを削除する。

    Returns:
        True: 削除成功
        False: ユーザーなし
    """

    user = get_user(db, username)

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True