import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { MediaType } from '@/models/media';

@Injectable({
  providedIn: 'root'
})

export class NavigationService {
  private readonly router = inject(Router);

  goToThumbnailPage(
    month: number,
    tag: string,
    section: string,
    favorite: boolean
  ): void {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }

    const queryParams = { favorite: favorite };

    let commands: (string | number)[];

    if (month !== 0) {
      commands = ['/month', month];
    } else if (tag === "" && section === "") {
      commands = ['/playlist'];
    } else if (section !== "") {
      commands = ['/tag', tag, 'section', section];
    } else {
      commands = ['/tag', tag];
    }

    this.router.navigate(commands, { queryParams });
  }

  goToMediaPage(
    mediaType: MediaType,
    month: number,
    tag: string,
    section: string,
    id: string,
    favorite: boolean
  ) {
    document.documentElement.requestFullscreen();

    const commands =
      month !== 0
        ? ["/month", String(month), mediaType]
        : ["/tag", tag, "section", section, mediaType];

    this.router.navigate(commands, {
      queryParams: { file: id, favorite: favorite },
    });
  }

  goToLoginPage() {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
    this.router.navigate(["/login"])
  }
}