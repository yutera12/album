import { Component, input, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Media } from '@/models/media'
import { environment } from '@/../environment'
import { NavigationService } from "@/services/navigation.service";
import { EditService } from "@/services/edit.service"
import { MediaService } from "@/services/media.service";
import { AuthService } from "@/services/auth.service"

@Component({
  selector: "app-grid",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./grid.component.html",
  styleUrl: './grid.component.scss'
})
export class GridComponent {
  private readonly targetAspectRatio = 16 / 9;

  private readonly mediaService = inject(MediaService)
  private readonly navigationService = inject(NavigationService)
  private readonly editService = inject(EditService)
  private readonly authService = inject(AuthService)

  readonly month = input.required<number>()
  readonly tag = input.required<string>()
  readonly section = input.required<string>()
  readonly favorite = input.required<boolean>();
  readonly items = input.required<Media[]>()
  readonly mediaType = input.required<string>()
  readonly tagList = this.editService.tagList
  readonly isAdmin = this.authService.isAdmin

  // サムネイル画像のURL
  src(item: Media): string {
    return environment.apiUrl + '/thumbnail/' + item.type + '/' + item.id;
  }

  // サムネイル画像クリック時の画面遷移
  onImageClick(id: string, title: string | null){
    const mediaType = this.mediaType();
    if (mediaType === "photo" || mediaType === "video"){
      this.navigationService.goToMediaPage(mediaType, this.month(), this.tag(), this.section(), id, this.favorite());
    } else {
      if (title !== null){
        if (this.tag() === "") {
          this.navigationService.goToThumbnailPage(0, title, '', this.favorite())
        } else {
          this.navigationService.goToThumbnailPage(0, this.tag(), title, this.favorite())
        }
      }
    }
  }

  // お気に入り操作
  favoriteToggle(v: Media, event: Event): void{
    const checked = (event.target as HTMLInputElement).checked;
    if (v.favorite === checked){
      return;
    }
    this.editService.setFavorite(v.fileName, checked, v.type).subscribe({
      next: (_) => {
        this.mediaService.reload()
      },
      error: (err) => {
        console.error("失敗", err);
      }
    });
  }

  // タグ編集操作
  tagToggle(v: Media, tag: string, event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    const updatedTag = checked
      ? [...new Set([...v.tag, tag])]
      : v.tag.filter(t => t !== tag);
    this.editService.setTag(v.fileName, updatedTag, v.type).subscribe({
      next: (_) => {
        this.mediaService.reload()
      },
      error: (err) => {
        console.error("失敗", err);
      }
    });
  }

  // 基準アスペクト比との差を補正し、異なる縦横比の画像を並べた際の
  // 見た目の大きさ（表示面積）が揃うよう左右余白を算出する。
  calcAspectFitMargin(aspectRatio: number) {
    let margin = ((1 - Math.sqrt(aspectRatio / this.targetAspectRatio)) / 2) * 100;
    if (margin < 0) margin = 0;

    return {
      marginLeft: margin + "%",
      marginRight: margin + "%",
    };
  }

   // 秒数を「○時間○分○秒」の日本語表記に変換する。
   // 例:
   // - 3661 => "1時間1分1秒"
   // - 60 => "1分"
   // - 59 => "59秒"
  formatSecondsToJapaneseTime(x: number): string {
    x = Math.floor(x);

    const h = Math.floor(x / 3600);
    const r = x % 3600;
    const m = Math.floor(r / 60);
    const s = r % 60;

    let ret = "";
    if (h > 0) ret += `${h}時間`;
    if (m > 0) ret += `${m}分`;
    if (s > 0) ret += `${s}秒`;

    return ret;
  }

  displayDateTime(): Boolean {
    if (this.month() !== 0){
      return true
    }
    if (this.section() !== ""){
      return true
    }
    return false

  }

}