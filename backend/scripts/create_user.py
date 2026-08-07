from getpass import getpass
from pwdlib import PasswordHash

from database.database import Base, engine, SessionLocal
from database.user_repository import create_user


# データベーステーブルを作成する。
# 既存テーブルがある場合は変更せず、そのまま利用する。
Base.metadata.create_all(bind=engine)


def main():
    """
    ユーザーを対話形式で作成する。

    ユーザー名、パスワード、管理者権限を入力し、
    パスワードをハッシュ化してデータベースへ登録する。
    """

    # ユーザー名を入力
    username = input("Username: ")

    # パスワード確認
    while True:
        password = getpass("Password: ")
        password_confirm = getpass("Confirm password: ")

        if password != password_confirm:
            print("Passwords do not match. Please try again.")
            continue

        if password == "":
            print("Password cannot be empty.")
            continue

        break

    # 管理者権限を入力
    while True:
        is_admin = input("Admin? (true or false): ").strip().lower()

        if is_admin == "true":
            is_admin = True
            break

        if is_admin == "false":
            is_admin = False
            break

        print("true または false を入力してください。")

    # 平文パスワードは保存せず、ハッシュ化して保存する
    hashed_password = PasswordHash.recommended().hash(password)

    # ユーザー情報を登録
    with SessionLocal() as db:
        create_user(
            db,
            username,
            is_admin,
            hashed_password,
        )


if __name__ == "__main__":
    main()