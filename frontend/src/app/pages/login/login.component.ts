import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

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
      error: (err) => {
        console.error(err);
        this.password.set('');
        this.errorMessage.set('ユーザー名またはパスワードが違います');
      },
    });
  }
}
