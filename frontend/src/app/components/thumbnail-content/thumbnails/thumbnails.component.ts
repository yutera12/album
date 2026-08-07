import { Component, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MediaService } from "../../../services/media.service";
import { GridComponent } from "./grid/grid.component"

@Component({
  selector: "app-thumbnails",
  standalone: true,
  imports: [CommonModule, GridComponent],
  templateUrl: "./thumbnails.component.html",
  styleUrl: './thumbnails.component.scss'
})
export class Thumbnails {
  private readonly mediaService = inject(MediaService);
  readonly month = this.mediaService.month
  readonly tag = this.mediaService.tag
  readonly section = this.mediaService.section
  readonly favorite = this.mediaService.favorite
  readonly videos = this.mediaService.videos;
  readonly photos = this.mediaService.photos;
  readonly thumbnails = this.mediaService.thumbnails;
}