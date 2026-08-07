import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { toSignal } from '@angular/core/rxjs-interop';
import { Birthday, YearMonthMap } from '../models/timeline';
import { shareReplay } from 'rxjs';
import { environment } from '../../environment';

@Injectable({ providedIn: 'root' })
export class TimelineService {
  private readonly http = inject(HttpClient);

  readonly birthdays = toSignal(
    this.http.get<Birthday[]>(`${environment.apiUrl}/birthdays`)
      .pipe(shareReplay(1)),  // キャッシュ
    { initialValue: [] }
  );

  readonly yearMonthMaps = toSignal(
    this.http.get<YearMonthMap[]>(
      `${environment.apiUrl}/year-month-map`
    ).pipe(shareReplay(1)),  // キャッシュ,
    { initialValue: [] }
  );
}