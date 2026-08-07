import { Component, input, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Media } from "../../../models/media"
import { mediaUrl } from "../media-url"

@Component({
  selector: "app-photo",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./photo.component.html",
  styleUrl: "../style.scss"
})

export class PhotoComponent {
  // 親コンポーネントから受け取る写真データ
  readonly item = input.required<Media>();

  // 写真URL
  readonly src = computed(() => mediaUrl(this.item()));
}