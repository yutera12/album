from pathlib import Path
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from paths import DATABASE_PATH

# ==========================================================
# プロジェクトのディレクトリ設定
# ==========================================================
DATABASE_URL = f"sqlite:///{DATABASE_PATH}" # SQLAlchemyが使用する接続URL

# ==========================================================
# データベース接続設定
# ==========================================================

# データベースエンジンを作成する。
# エンジンは「どのDBへ、どう接続するか」を管理するオブジェクト。
engine = create_engine(
    DATABASE_URL,

    # SQLiteはデフォルトでは
    # 「作成したスレッド以外から接続を使えない」
    # という制限があるため、FastAPIで利用できるよう無効化する。
    connect_args={"check_same_thread": False},
)


# ==========================================================
# セッション設定
# ==========================================================

# Sessionを作成するためのファクトリ。
# SessionはSQLを発行したり、commit・rollbackを管理する。
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,        # commitするまでDBへ反映しない
    autocommit=False,       # commit()を自分で呼ぶまで自動コミットしない
)


# ==========================================================
# モデルの親クラス
# ==========================================================

# ORMモデル(Userなど)が継承する基底クラス。
Base = declarative_base()


# ==========================================================
# FastAPI用 DBセッション取得
# ==========================================================

def get_db() -> Generator[Session, None, None]:
    """
    リクエストごとにDBセッションを生成し、
    処理が終わったら必ず閉じる。

    FastAPIでは Depends(get_db) として利用する。

    Yields:
        Session: SQLAlchemyのデータベースセッション
    """

    # セッションを作成
    db = SessionLocal()

    try:
        # エンドポイントへセッションを渡す
        yield db

    finally:
        # リクエスト終了後に必ず接続を閉じる
        db.close()