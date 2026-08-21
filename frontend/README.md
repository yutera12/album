# Frontend

アルバムアプリのフロントエンド（Angular）です。

## ディレクトリ構成

```
src/
├── app/
│   ├── models/         # 型定義
│   ├── pages/          # 画面単位のコンポーネント
│   │   ├── login/        # ログイン画面
│   │   ├── thumbnail/    # サムネイル画面
│   │   └── media/        # メディア再生画面
│   │
│   ├── services/
│   │   ├── interceptors/   # HTTPリクエスト/レスポンスを横断的に加工するインターセプター群
│   │   │   ├── auth-interceptor.service.ts   # HTTPリクエストにJWTトークンを付与し、
│   │   │   │                                 # 401エラーが返ったらトークンを削除してログイン画面へ戻す
│   │   │   └── camel-case-interceptor.service.ts  # APIレスポンスのキーをスネークケースからキャメルケースに変換
│   │   │
│   │   ├── guards/         # ルート遷移の可否を判定するガード群
│   │   │   └── auth-guard.service.ts     # 未ログインならログイン画面へ遷移させ、
│   │   │                                 # ログイン済みならそのままルート遷移を許可するガード
│   │   │
│   │   ├── auth.service.ts         # ログイン・ログアウト・認証状態・管理者権限を管理するサービス
│   │   ├── edit.service.ts         # メディアのタグ・お気に入りを編集するサービス
│   │   ├── media.service.ts        # メディア一覧を取得・フィルタリングし、状態を管理するサービス
│   │   ├── navigation.service.ts   # 画面遷移（ルーティング）を一元管理するサービス
│   │   └── timeline.service.ts     # 誕生日や年月マップなど、タイムライン情報を取得・管理するサービス
│   │
│   ├── app.config.ts   # Angularアプリ全体のルーティング・HTTP通信・Interceptorなどの設定をまとめる設定ファイル
│   ├── app.routes.ts   # URLと表示するコンポーネント、認証ガードの対応関係を設定するルーティング定義
│   └── app.ts          # ルーティングに応じたページを表示するアプリのルートコンポーネント
│
├── environment.ts      # 設定値（バックエンドのURL）を定義するファイル
├── index.html          # アプリ全体のエントリーポイントとなるHTMLファイル
├── main.ts             # アプリケーションを起動するエントリーポイントファイル
└── style.scss          # アプリ全体に適用するグローバルスタイルを定義するファイル
```

## 設定

`src/environment.ts` でバックエンドのAPI URLと編集モードを設定します。

```ts
export const environment = {
  apiUrl: "http://localhost:10000",  // バックエンドのURL
};
```

バックエンドのポートを変更した場合は、ここも合わせて変更してください。
