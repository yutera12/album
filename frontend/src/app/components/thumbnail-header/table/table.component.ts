import { Component, inject, input } from "@angular/core";
import { CommonModule } from "@angular/common";
import { TimelineService } from '../../../services/timeline.service';
import { NavigationService } from "../../../services/navigation.service";
import { MediaService } from "../../../services/media.service";

@Component({
  selector: 'table-month',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './table.component.html',
  styleUrl: './table.component.scss'
})
export class TableComponent {
  // レイアウトを決める定数
  readonly monthTabWidth = input.required<number>();
  readonly playlistTabWidth = input.required<number>();

  // DI
  private readonly mediaService = inject(MediaService)
  private readonly timelineService = inject(TimelineService);
  private readonly navigationService = inject(NavigationService);

  // 
  readonly month = this.mediaService.month
  readonly favorite = this.mediaService.favorite
  readonly yearMonthMaps = this.timelineService.yearMonthMaps;

  // ページ遷移関数
  goToPlaylistPage() {
    this.navigationService.goToThumbnailPage(0, '', '', this.favorite());
  }
  goToMonthPage(year: number, month: number) {
    this.navigationService.goToThumbnailPage(year * 100 + month, '', '', this.favorite());
  }
}