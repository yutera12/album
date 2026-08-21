import { CanActivateFn } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '@/services/auth.service';
import { NavigationService } from '@/services/navigation.service';

export const authGuard: CanActivateFn = () => {

  const navigationService = inject(NavigationService)
  const auth = inject(AuthService);

  if(auth.isLoggedIn()){
    return true;
  }

  navigationService.goToLoginPage();
  return false;

};