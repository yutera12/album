import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient,withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { authInterceptor } from './services/interceptors/auth-interceptor.service';
import { camelCaseInterceptor } from './services/interceptors/camel-case-interceptor.service';

export const appConfig: ApplicationConfig = {
  providers: [

    // 予期しないエラーをAngularのエラーハンドラへ渡す
    provideBrowserGlobalErrorListeners(),

    // ルーティング（画面遷移）の設定を登録
    provideRouter(routes),

    // HttpClientを使用できるようにする
    provideHttpClient(

      // すべてのHTTP通信でInterceptorを実行する
      withInterceptors([

        // HTTPリクエスト送信前にJWTアクセストークンを付与する
        // （ログイン済みの場合）
        authInterceptor,

        // HTTPレスポンス受信後にsnake_caseのキーをcamelCaseへ変換する
        camelCaseInterceptor
      ])
    )
  ]
};