import { Component, HostListener, inject, signal, computed, ViewChild, effect } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { NavigationService } from "@/services/navigation.service";
import { MediaService } from "@/services/media.service";
import { PhotoComponent } from "./content/photo/photo.component";
import { VideoComponent } from "./content/video/video.component";
import { MediaType } from "@/models/media";

@Component({
  selector: "app-media",
  standalone: true,
  imports: [CommonModule, PhotoComponent, VideoComponent],
  templateUrl: "./media.component.html",
  styleUrl: "./media.component.scss"
})
export class MediaComponent {
  /* -------------------- */
  /* DI / ViewChild */
  /* -------------------- */
  @ViewChild(VideoComponent)
  video!: VideoComponent;

  private readonly navigationService = inject(NavigationService);
  private readonly mediaService = inject(MediaService);
  private readonly route = inject(ActivatedRoute);

  /* -------------------- */
  /* Route Params (Signals) */
  /* -------------------- */
  private readonly paramMap = toSignal(this.route.paramMap);
  private readonly queryParamMap = toSignal(this.route.queryParamMap);
  private readonly month = computed(() => Number(this.paramMap()?.get('month') ?? 0));
  private readonly tag = computed(() => String(this.paramMap()?.get('tag') ?? ''));
  private readonly section = computed(() => String(this.paramMap()?.get('section') ?? ''));
  private readonly currentMediaId = computed(() => this.queryParamMap()?.get('file') ?? '');
  readonly mediaType = computed<MediaType>(() =>
    this.paramMap()?.get('mediaType') === 'video'
    ? 'video'
    : 'photo'
  );
  private readonly favorite = computed(() =>
    this.queryParamMap()?.get("favorite") !== "false"
  );

  /* -------------------- */
  /* Derived State */
  /* -------------------- */
  readonly currentItem = computed(() =>
    this.mediaService.getMedia(
      this.mediaType(),
      this.currentMediaId(),
      0
    )
  );

  /* -------------------- */
  /* UI State */
  /* -------------------- */
  readonly tooltip = signal(false);

  /* -------------------- */
  /* Lifecycle */
  /* -------------------- */
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


  /* -------------------- */
  /* Keyboard Event */
  /* -------------------- */
  @HostListener("document:keydown", ["$event"])
  handleKeyboardEvent(event: KeyboardEvent) {
    if (event.key === "ArrowUp") {
      this.returnToThumbnailPage();
    } else if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
      const nextMedia = this.mediaService.getMedia(
        this.mediaType(),
        this.currentMediaId(),
        event.key === "ArrowRight" ? 1 : -1
      );
      if (!nextMedia) {
        return;
      }
      this.navigationService.goToMediaPage(this.mediaType(), this.month(), this.tag(), this.section(), nextMedia.id, this.favorite());
    } else if (event.key === "ArrowDown") {
      if (this.mediaType() === "video") {
        this.video?.resetPlaybackPosition();
      }
    }
  }

  /* --------------- */
  /* Page 遷移イベント */
  /* -----------------*/
  returnToThumbnailPage() {
    this.navigationService.goToThumbnailPage(
      this.month(),
      this.tag(),
      this.section(),
      this.favorite()
    );
  }

  /* -------------------- */
  /* UI Handlers */
  /* -------------------- */
  mover = () => {
    this.tooltip.set(true);
  };

  mleave = () => {
    this.tooltip.set(false);
  };
}