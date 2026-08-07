import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { environment } from '../../environment';
import { MediaType } from '../models/media';


@Injectable({providedIn: 'root'})
export class EditService {
  private readonly http = inject(HttpClient);

  readonly tagList = toSignal(
    this.http.get<string[]>(`${environment.apiUrl}/tag-list`),
    { initialValue: [] }
  );

  // readonly isAdmin = toSignal(
  //   this.http.get<boolean>(`${environment.apiUrl}/is-admin`),
  //   { initialValue: false }
  // )



  setTag(
    fileName: string,
    tags: string[],
    type: MediaType
  ) {
    return this.http.post(
      `${environment.apiUrl}/set-tag`,
      {
        fileName,
        tags,
        type
      }
    );
  }

  setFavorite(fileName: string, favorite: boolean, type: MediaType) {
    return this.http.post(
      `${environment.apiUrl}/set-favorite`,
      {
        fileName,
        favorite,
        type
      }
    );
  }
}


