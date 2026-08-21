import { Component, inject, effect, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ActivatedRoute } from '@angular/router';
import { HeaderComponent } from "./header/thumbnail-header.component";
import { MediaService } from "@/services/media.service";
import { FormsModule } from '@angular/forms';
import { BreadcrumbsComponent } from "./content/breadcrumbs/breadcrumbs.component"
import { TitleComponent } from "./content/title/title.component"
import { ToggleSwitchComponent } from "./content/toggle-switch/toggle-switch.component"
import { Thumbnails } from "./content/thumbnails/thumbnails.component";
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: "app-thumbnail",
  standalone: true,
  imports: [CommonModule, HeaderComponent, FormsModule, Thumbnails, BreadcrumbsComponent, TitleComponent, ToggleSwitchComponent],
  templateUrl: "./thumbnail.component.html",
  styleUrl: "./thumbnail.component.scss"
})
export class ThumbnailComponent {
  // ===== DI =====
  private readonly mediaService = inject(MediaService);
  private readonly route = inject(ActivatedRoute);
  private readonly queryParamMap = toSignal(this.route.queryParamMap);

  // Route parameters
  paramMap = toSignal(this.route.paramMap);
  readonly month = computed(() =>
    Number(this.paramMap()?.get('month') ?? 0)
  );
  readonly tag = computed(() =>
    this.paramMap()?.get('tag') ?? ''
  );
  readonly section = computed(() =>
    this.paramMap()?.get('section') ?? ''
  );
  readonly favorite = computed(() =>
    this.queryParamMap()?.get("favorite") === "true"
  );

  // Route parametersを反映
  constructor() {
    effect(() => {
      if (this.month() !== 0) {
        this.mediaService.setMonth(this.month());
      } else {
        this.mediaService.setTagSection(
          this.tag(),
          this.section()
        );
      }
      this.mediaService.setFavorite(this.favorite())
    });
  }

  scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

}