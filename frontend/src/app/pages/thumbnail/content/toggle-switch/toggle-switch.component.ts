import { Component, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MediaService } from "@/services/media.service";
import { NavigationService } from "@/services/navigation.service";


@Component({
  selector: "app-toggle-switch",
  standalone: true,
  imports: [CommonModule, MatSlideToggleModule],
  templateUrl: "./toggle-switch.component.html",
  styleUrl: "./toggle-switch.component.scss"
})
export class ToggleSwitchComponent {
  private readonly mediaService = inject(MediaService)
  private readonly navigationService = inject(NavigationService)

  private readonly month = this.mediaService.month
  private readonly tag = this.mediaService.tag
  private readonly section = this.mediaService.section
  readonly favorite = this.mediaService.favorite

  onToggleChange(checked: boolean){
    this.mediaService.setFavorite(checked)
    this.navigationService.goToThumbnailPage(this.month(), this.tag(), this.section(), this.favorite())
  }
}