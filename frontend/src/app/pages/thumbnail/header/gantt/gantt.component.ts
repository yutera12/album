import { Component, inject, input, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { TimelineService } from "@/services/timeline.service";
import { YearMonthMap } from "@/models/timeline";


const MAX_AGE = 150;

@Component({
  selector: 'gantt',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gantt.component.html',
  styleUrl: './gantt.component.scss'
})
export class GanttComponent {
  // レイアウトを決定する定数
  readonly monthTabWidth = input.required<number>();
  readonly playlistTabWidth = input.required<number>();
  readonly lineGapX = input.required<number>();
  readonly lineGapY = input.required<number>();
  readonly legendMarginTop = input.required<number>();

  // DI
  private readonly timelineService = inject(TimelineService);
  private readonly yearMonthMaps = this.timelineService.yearMonthMaps;


  // 月数 (= Playlistを除くセル数）のsignal
  private readonly totalMonths = computed(() =>
    this.yearMonthMaps().reduce(
      (sum, item) => sum + item.months.length,
      0
    )
  );


  private dateToSlotPosition(year: number, month: number, day: number, yearMonthMap: YearMonthMap[]): number {
    // """
    // 日付（year, month, day）を入力すると、画面上部の横軸のどの位置に相当するかを返す

    // 例
    // yearMonthMap = [
    //   {"year": 2020, "months": [10, 12]},
    //   {"year": 2021, "months": [2020, 2021]}
    // ]

    // year, mont, day | return
    // --------------- | -----
    //       0,  0,  0 | -1     # 0が入力されたら-1を返す
    //    2020,  9, 10 | 0      # 2020/09/10は2000/10の箱（一つ目の箱）よりも前なので0
    //    2020, 10, 10 | 0.333  # 2020/10/10は2000/10の箱の中の1/3の位置に相当するので、1/3
    //    2020, 11, 10 | 1      # 2020/11/10は2000/10の箱と2020/12の箱の間に相当するので1
    //    2020, 12, 10 | 1.333
    //    2021, 01, 10 | 2.333
    //    2021, 02, 10 | 3.333
    //    2021, 03, 10 | -1     # 2021/03/10は最後の箱(2021/2の箱)の外側に相当するので-1
    // """


    // 0,0,0が入力されたら-1を返す
    if (year === 0 && month === 0 && day === 0) {
      return -1;
    }

    let pos = 0;

    for (const entry of yearMonthMap) {
      const y = entry.year;
      for (const m of entry.months) {
        // 箱の年月を整数で表現（YYYYMM）
        const slotYYYYMM = y * 100 + m;
        const inputYYYYMM = year * 100 + month;

        if (slotYYYYMM === inputYYYYMM) {
          // 箱内の位置：日数/30で相対位置を計算
          return pos + day / 30;
        } else if (slotYYYYMM > inputYYYYMM) {
          // 入力日がこの箱より前なら現在のposを返す
          return pos;
        }
        pos += 1;
      }
    }

    // 全ての箱より後の場合
    return -1;
  }

  readonly infoGant = computed(() => {
    const maps = this.yearMonthMaps();
    const result = [];

    for (const person of this.timelineService.birthdays()) {

      const data: { label: string; x1: number; x2: number }[] = [];

      for (let age = 0; age < MAX_AGE; age++) {

        if (person.year + age > maps[maps.length - 1].year) {
          break;
        }

        const x1 = this.dateToSlotPosition(
          person.year + age,
          person.month,
          person.day,
          maps
        );

        const x2 = this.dateToSlotPosition(
          person.year + age + 1,
          person.month,
          person.day,
          maps
        );

        if (x1 === 0 && x2 === 0) {
          continue;
        }

        data.push({ label: `${person.name} ${age}歳`, x1, x2 });
      }

      result.push({
        name: person.name,
        gant: data
      });
    }

    return result;
  });
  
  /**
   * line / legend 共通の位置計算（width, marginLeft, 基準となるmarginTop）
   */
  private getBasePosition(x1: number, x2: number, num: number) {
    if (x2 < 0) {
      x2 = this.totalMonths();
    }

    const width = (x2 - x1) * this.monthTabWidth() - this.lineGapX() + 'px';
    const marginLeft = x1 * this.monthTabWidth() + this.playlistTabWidth() + 'px';
    const marginTopBase = num * this.lineGapY();

    return { width, marginLeft, marginTopBase };
  }

  /**
   * ガントの「線」の位置
   */
  getLinePosition(x1: number, x2: number, num: number) {
    const { width, marginLeft, marginTopBase } = this.getBasePosition(x1, x2, num);

    return {
      width,
      marginLeft,
      marginTop: marginTopBase + 'px'
    };
  }

  /**
   * ガントの「凡例（ラベル）」の位置
   */
  getLegendPosition(x1: number, x2: number, num: number) {
    const { width, marginLeft, marginTopBase } = this.getBasePosition(x1, x2, num);

    return {
      width,
      marginLeft,
      marginTop: marginTopBase + this.legendMarginTop() + 'px'
    };
  }
}
//   getGanttPosition(x1:number, x2:number, num:number, line:boolean) {
//     if (x2 < 0){
//       x2 = this.totalMonths()
//     }
//     const width = (x2 - x1) * this.monthTabWidth() - this.lineGapX() + 'px';
//     const marginLeft = x1 * this.monthTabWidth() + this.playlistTabWidth() + 'px';
//     const marginTop = line
//       ? num * this.lineGapY() + 'px'
//       : num * this.lineGapY() + this.legendMarginTop() + 'px';

//     return {
//       width,
//       marginLeft,
//       marginTop
//     };
//   }
// }