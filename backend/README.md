# Backend

アルバムアプリのバックエンド（FastAPI）です。

## ディレクトリ構成

```
backend/
├── assets/                   # ユーザが用意するファイル（Git管理外）
│   ├── media/                  # メディアファイル（画像・動画）
│   └── info.json               # メディアのメタデータ
├── data/                     # main.pyやスクリプトの実行によって生成されるデータ（Git管理外）
│   ├── app.db                  # ユーザ管理用SQLite DB（再生成不可）
│   ├── info_photo_cache.json   # 画像のメタデータのキャッシュファイル（削除してもmain.pyの実行により再生成）
│   ├── info_video_cache.json   # 動画のメタデータのキャッシュファイル（削除してもmain.pyの実行により再生成）
│   └── thumbnails/             # サムネイルデータ（削除してもmain.pyの実行により再生成）
├── database/                 # ユーザ管理用SQLite DBの操作
│   ├── database.py             # ユーザ管理用SQLite DB操作のためのDB接続・セッション管理を設定するコード
│   └── user_repository.py      # ユーザ管理用SQLite DB操作（CRUD）を担当するコード
├── models/                   # データの構造を定義
│   ├── api_model.py            # Pydanticモデル
│   └── auth_models.py          # SQLAlchemyモデル
├── queries/                  # データから必要な情報を検索・抽出する処理
│   ├── media.py                # メディアの月別・タグ別フィルタリング処理
│   └── tag.py                  # info.jsonに記されたtag情報の中から必要箇所を取得する処理
├── samples/                  # メディアファイルとinfo.jsonのサンプル
├── scripts/                  # 管理用スクリプト（ユーザー作成・一覧確認）
├── services/                 # 認証・前処理・サムネイル生成・タグ更新などのロジック
│   ├── auth.py                 # JWTベースの認証機能
│   ├── preprocess.py           # メディアのメタデータ、サムネイル作成などの前処理
│   ├── security.py             # 認証回りの設定を記載
│   ├── thumbnail.py            # タグ、セクション毎の代表サムネイルをルールに従い選択する機能
│   └── update.py               # info.jsonの更新機能
├── utils/                    # 共通処理
│   ├── date_utils.py           # 日付関係の共通処理
│   ├── file_utils.py           # ファイル関係の共通処理
│   ├── image_utils.py          # 画像関係の共通処理
│   ├── time_utils.py           # 時刻関係の共通処理
│   └── json_store_utils.py     # JSONデータの読み書き、メディアのメタデータ（アスペクト比など）のキャッシュを作成するロジック
├── .env                      # 環境変数ファイル（Git管理外）
├── main.py                   # エントリーポイント（FastAPIアプリ本体）
└── logging_config.py         # ログの設定
```


## 環境変数

| 変数名 | 説明 | 必須 |
|---|---|---|
| `SECRET_KEY` | JWT署名用の秘密鍵（`secrets.token_hex(32)` で生成） | ✅ |

## API ドキュメント

起動後、以下でSwagger UIを確認できます。

http://localhost:10000/docs

## スクリプト

- `uv run python -m scripts.create_user` — ユーザー作成（対話形式でユーザー名・パスワード・管理者権限を入力）
- `uv run python -m scripts.list_users` — ユーザー一覧確認

## 起動時の前処理について

起動時（`lifespan`）に一度だけ `preprocess()` が実行され、`assets/media/` 内のファイルと `info.json` の整合性チェック、サムネイル生成、動画メタデータ（`ffprobe` 使用）の取得が行われます。ファイルを追加・変更した場合は、サーバーの再起動が必要です。
