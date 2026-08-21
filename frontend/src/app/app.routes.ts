import { Routes } from '@angular/router';
import { ThumbnailComponent } from './pages/thumbnail/thumbnail.component';
import { MediaComponent } from './pages/media/media.component';
import { LoginComponent } from './pages/login/login.component'
import { authGuard } from './services/guards/auth-guard.service';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'playlist', component: ThumbnailComponent, canActivate: [authGuard] },
  { path: '', redirectTo: 'playlist', pathMatch: 'full' },
  { path: 'month/:month', component: ThumbnailComponent, canActivate: [authGuard] },
  { path: 'tag/:tag', component: ThumbnailComponent, canActivate: [authGuard] },
  { path: 'tag/:tag/section/:section', component: ThumbnailComponent, canActivate: [authGuard] },
  { path: 'month/:month/:mediaType', component: MediaComponent, canActivate: [authGuard] },
  { path: 'tag/:tag/section/:section/:mediaType', component: MediaComponent, canActivate: [authGuard] },
];