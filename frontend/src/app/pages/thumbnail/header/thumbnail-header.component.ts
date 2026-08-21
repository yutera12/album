import { Component, inject, input } from "@angular/core";
import { CommonModule } from "@angular/common";
import { TableComponent } from './table/table.component'
import { GanttComponent } from './gantt/gantt.component'
import { TimelineService } from "@/services/timeline.service";
import { AuthService } from "@/services/auth.service";

@Component({
    selector: 'app-header',
    standalone: true,
    imports: [CommonModule, TableComponent, GanttComponent],
    templateUrl: './thumbnail-header.component.html',
    styleUrl: './thumbnail-header.component.scss'
})
export class HeaderComponent {
  // レイアウト定数
  readonly monthTabWidth = 30;
  readonly playlistTabWidth = 100;
  readonly baseHeight = 70;
  readonly lineGapX = 4;
  readonly lineGapY = 20;
  readonly legendMarginTop = 2;

  // DI
  private readonly timelineService = inject(TimelineService);
  private readonly authService = inject(AuthService)

  // 
  readonly birthdays = this.timelineService.birthdays;

  logout() {
    this.authService.logout()
  }
}

