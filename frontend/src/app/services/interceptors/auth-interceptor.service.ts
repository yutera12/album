import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem("token");
  const router = inject(Router);
  if(token){
    req = req.clone({
      setHeaders:{
        Authorization: `Bearer ${token}`
      }
    });
  }
  return next(req).pipe(
    catchError(error => {
      if (error.status === 401) {
        // トークン削除
        localStorage.removeItem("token");

        // ログインページへ移動
        router.navigate(['/login']);
      }

      return throwError(() => error);
    })
  );;

};