import { Component, inject } from "@angular/core";
import { NavigationService } from "../../../services/navigation.service";
import { MediaService } from "../../../services/media.service";

@Component({
  selector: 'app-breadcrumbs',
  standalone: true,
  templateUrl: './breadcrumbs.component.html',
  styleUrl: './breadcrumbs.component.scss'
})
export class BreadcrumbsComponent {
  private readonly mediaService = inject(MediaService)
  private readonly navigationService = inject(NavigationService);

  readonly month = this.mediaService.month
  readonly tag = this.mediaService.tag
  readonly section = this.mediaService.section
  readonly favorite = this.mediaService.favorite

  goToThumbnailPage(tag: string) {
    this.navigationService.goToThumbnailPage(
      0, tag, '', this.favorite()
    );
  }
}