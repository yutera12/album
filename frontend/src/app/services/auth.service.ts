import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { tap } from 'rxjs';
import { environment } from '../../environment';
import { NavigationService } from './navigation.service';

@Injectable({providedIn: 'root'})
export class AuthService {

  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService)
  private readonly apiUrl = environment.apiUrl;
  private readonly adminSignal = signal(false);
  readonly isAdmin = this.adminSignal.asReadonly();

  constructor() {
    if (this.isLoggedIn()) {
      this.checkAdmin();
    }
  }

  login(username: string, password: string) {

    const body = new HttpParams()
      .set('username', username)
      .set('password', password);

    return this.http.post<any>(
      `${this.apiUrl}/token`,
      body.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    ).pipe(
      tap(res => {
        localStorage.setItem('token', res.accessToken);
        this.checkAdmin();
      })
    );
  }

  checkAdmin() {
    this.http.get<boolean>(
      `${environment.apiUrl}/is-admin`
    )
    .subscribe({
      next: (value) => {
        this.adminSignal.set(value);
      },
      error: () => {
        this.adminSignal.set(false);
      }
    });
  }

  logout() {
    localStorage.removeItem('token');
    this.navigationService.goToLoginPage();
    this.adminSignal.set(false);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  isLoggedIn(): boolean {
    return this.getToken() !== null;
  }

  getCurrentUser() {
    return this.http.get<{ username: string }>(
      `${this.apiUrl}/users/me/`
    );
  }
}