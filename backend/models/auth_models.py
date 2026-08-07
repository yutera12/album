from sqlalchemy import Column, Integer, String, Boolean

from database.database import Base


class User(Base):
    """
    ユーザー情報を保持するデータベースモデル。

    Attributes
    ----------
    id : int
        ユーザーID。
        自動採番される主キー。

    username : str
        ログインユーザー名。
        ユニーク制約があり、重複したユーザー名は登録できない。

    is_admin : bool
        管理者権限の有無。
        Trueの場合、管理者向け操作を許可する。

    hashed_password : str
        ハッシュ化されたパスワード。
        平文パスワードは保存しない。
    """

    __tablename__ = "users"

    # ユーザーID（主キー）
    id = Column(
        Integer,
        primary_key=True
    )

    # ログインユーザー名（一意）
    username = Column(
        String,
        unique=True,
        nullable=False
    )

    # 管理者権限フラグ
    is_admin = Column(
        Boolean,
        nullable=False
    )

    # ハッシュ化済みパスワード
    hashed_password = Column(
        String,
        nullable=False
    )