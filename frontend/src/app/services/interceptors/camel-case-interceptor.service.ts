import { HttpInterceptorFn } from '@angular/common/http';
import { map } from 'rxjs/operators';
import camelcaseKeys from 'camelcase-keys';

export const camelCaseInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    map(event => {
      if (event.type === 4 /* HttpEventType.Response */ && event.body) {
        return event.clone({
          body: camelcaseKeys(event.body, { deep: true })
        });
      }
      return event;
    })
  );
};