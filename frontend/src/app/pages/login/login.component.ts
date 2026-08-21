import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';

import { AuthService } from '@/services/auth.service';
import { NavigationService } from '@/services/navigation.service';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
  imports: [
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly navigationService = inject(NavigationService);

  readonly hidePassword = signal(true);
  readonly username = signal('');
  readonly password = signal('');
  readonly errorMessage = signal('');

  login(): void {
    this.errorMessage.set('');

    this.auth.login(this.username(), this.password()).subscribe({
      next: () => {
        this.password.set('');
        this.navigationService.goToThumbnailPage(0, '', '', false);
      },
      error: (err: HttpErrorResponse) => {
        console.error(err);
        this.password.set('');

        if (err.status === 0) {
          // サーバーに接続できない（バックエンド未起動、ネットワーク断など）
          this.errorMessage.set('サーバーに接続できません');
        } else if (err.status === 401 || err.status === 403) {
          // 認証エラー
          this.errorMessage.set('ユーザー名またはパスワードが違います');
        } else {
          // その他のサーバーエラー
          this.errorMessage.set('エラーが発生しました');
        }
      },
    });
  }
}