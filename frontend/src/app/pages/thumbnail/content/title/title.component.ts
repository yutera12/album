import { Component, inject, computed } from '@angular/core';
import { Birthday } from '@/models/timeline';
import { TimelineService } from "@/services/timeline.service";
import { MediaService } from '@/services/media.service';


@Component({
  selector: 'app-title',
  standalone: true,
  templateUrl: './title.component.html',
  styleUrl: './title.component.scss'
})
export class TitleComponent {
  private readonly timelineService = inject(TimelineService);
  private readonly mediaService = inject(MediaService)

  private readonly birth = this.timelineService.birthdays;
  private readonly tag = this.mediaService.tag
  private readonly section = this.mediaService.section
  private readonly month = this.mediaService.month

  // 対象月時点での各人物の月齢範囲テキストを生成
  private getBirthText(yyyymm: number, birthdays: Birthday[]): string {
    const targetYear = Math.floor(yyyymm / 100);
    const targetMonth = yyyymm % 100;
    const targetTotalMonth = targetYear * 12 + targetMonth;

    return birthdays
      .map(({ name, year, month }) => {
        const birthTotalMonth = year * 12 + month;

        // 誕生月より前
        if (targetTotalMonth < birthTotalMonth) {
          return `${name}：誕生前`;
        }
        // 誕生月と同月
        if (targetTotalMonth === birthTotalMonth) {
          return `${name}：誕生前～0歳0ヵ月`;
        }

        // 誕生後：月齢を「◯歳◯ヵ月～◯歳◯ヵ月」の形式で表示
        const diff = targetTotalMonth - birthTotalMonth;
        const formatAge = (totalMonths: number) => {
          const y = Math.floor(totalMonths / 12);
          const m = totalMonths % 12;
          return `${y}歳${m}ヵ月`;
        };

        return `${name}：${formatAge(diff - 1)}～${formatAge(diff)}`;
      }).join("、");
  }

  // yyyymm 形式（例: 202401）を「2024年1月」に整形
  private formatYearMonth(yyyymm: number): string {
    const year = Math.floor(yyyymm / 100);
    const month = yyyymm - year * 100;
    return `${year}年${month}月`;
  }

  readonly displayBirthText = computed(() => (this.month() !== 0))

  readonly birthText = computed(() => this.getBirthText(this.month(), this.birth()));

  // ページタイトル（viewMode に応じて内容を切り替え）
  readonly pageTitle = computed(() => {
    if (this.month() !== 0) {
      return this.formatYearMonth(this.month());
    } else if (this.tag() === '') {
      return 'Playlist'
    } else if (this.section() === ''){
        return this.tag();
    } else {
        return `${this.tag()} > ${this.section()}`;
    }
  });
}