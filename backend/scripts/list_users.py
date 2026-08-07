from database.database import SessionLocal
from models.auth_models import User


def main() -> None:
    """
    登録されているユーザー情報を一覧表示する。

    データベースから全ユーザーを取得し、
    ID、ユーザー名、管理者権限を表示する。
    """

    # データベースセッションを作成
    with SessionLocal() as db:
        # usersテーブルから全ユーザーを取得
        users = db.query(User).all()

        for user in users:
            print(
                f"id={user.id}, "
                f"username={user.username}, "
                f"is_admin={user.is_admin}, "
            )


if __name__ == "__main__":
    main()