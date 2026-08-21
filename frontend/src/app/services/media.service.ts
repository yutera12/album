import { Injectable, inject, signal, Signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { switchMap, Observable, combineLatest, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Media } from '@/models/media';
import { FilterState } from '@/models/filter';
import { environment } from '@/../environment';


@Injectable({ providedIn: 'root' })
export class MediaService {

  private readonly http = inject(HttpClient);

  // ----------------------------------------------
  // Media, Thumbnailのフィルター条件を保持するSignal
  // ----------------------------------------------
  // month         : 月検索
  // tag           : タグ検索
  // section       : セクション検索
  // favorite      : お気に入りのみを表示するか
  //
  private readonly _filter = signal<FilterState>({
    month: 0,
    tag: "",
    section: "",
    favorite: false,
  });
  readonly month = computed(() => this._filter().month);
  readonly tag = computed(() => this._filter().tag);
  readonly section = computed(() => this._filter().section);
  readonly favorite = computed(() => this._filter().favorite);
  private readonly _reload = signal<number>(0);


  // ---------------------------------------------------------
  // Media一覧をフィルタ条件に応じて取得する共通Signal生成処理
  // ---------------------------------------------------------
  private createMediaSignal(endpoint: string): Signal<Media[]> {
    return toSignal(
      combineLatest([
        toObservable(this._filter),
        toObservable(this._reload)
      ]).pipe(

        switchMap(([filter, _]) => {
          const { month, tag, section, favorite } = filter;
          let request$: Observable<Media[]>;
          let params = {favorite: favorite}
          if (month) {
            request$ = this.http.get<Media[]>(
              `${endpoint}/month/${month}`, {params: params}
            );
          } else if (tag && section) {
            request$ = this.http.get<Media[]>(
              `${endpoint}/tag/${tag}/section/${section}`, {params: params}
            );
          } else {
            request$ = of([]);
          }

          return request$.pipe(
            catchError(() => of([] as Media[]))
          );
        })
      ),
      { initialValue: [] }
    );
  }


  // 再取得
  reload() {
    this._reload.update(v => v + 1);
  }

  // --------------------------
  // Media, ThumbnailののSignal
  // --------------------------
  readonly photos = this.createMediaSignal(`${environment.apiUrl}/photos`);
  readonly videos = this.createMediaSignal(`${environment.apiUrl}/videos`);
  readonly thumbnails = toSignal(
    combineLatest([
      toObservable(this._filter),
      toObservable(this._reload)
    ]).pipe(
      switchMap(([filter, _]) => {
        if (filter.month !== 0 || filter.section !== "") {
          return of([] as Media[]);
        }

        const url = filter.tag === ""
          ? "thumbnail-random"
          : `thumbnail-random/${filter.tag}`;

        return this.http.get<Media[]>(
          `${environment.apiUrl}/${url}`, {params: {favorite: filter.favorite}}
        ).pipe(
          catchError(() => of([] as Media[]))
        );;
      })
    ),
    { initialValue: [] }
  );



  // -----------------------------
  // フィルター変更メソッド
  // -----------------------------
  setMonth(month: number) {
    this._filter.update(f => ({
      ...f,
      month: month,
      tag: "",
      section: "",
    }));
  }

  setTag(tag: string) {
    this._filter.update(f => ({
      ...f,
      month: 0,
      tag: tag,
      section: "",
    }));
  }

  setTagSection(tag: string, section: string) {
    this._filter.update(f => ({
      ...f,
      month: 0,
      tag: tag,
      section: section,
    }));
  }

  setFavorite(favorite: boolean) {
    this._filter.update(f => ({
      ...f,
      favorite: favorite,
    }));
  }


  // =====================================================
  // 指定したメディアIDを基準に、前後の位置のメディアを取得する
  // =====================================================
  getMedia(mediaType: string, id: string, pos: number): Media {
    let medias: Media[] = [];
    if (mediaType === "photo"){
      medias = this.photos()
    } else if (mediaType === "video") {
      medias = this.videos()
    }  else {
      throw new Error(`Invalid mediaType`);
    }
    const mediaIndex = medias.findIndex(media => media.id === id);
    if (mediaIndex === -1) {
      throw new Error(`Media not found: ${id}`);
    }
    const mediaIndex_pos = Math.min(Math.max(mediaIndex + pos, 0), medias.length - 1);
    return medias[mediaIndex_pos]

  }
}
