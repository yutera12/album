import { Component, ElementRef, ViewChild, input, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Media } from "@/models/media"
import { mediaUrl } from "../media-url"

@Component({
  selector: "app-video",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./video.component.html",
  styleUrl: "../style.scss"
})
export class VideoComponent {
  // 親コンポーネントから受け取る動画データ
  readonly item = input.required<Media>();

  // 動画URL
  readonly src = computed(() => mediaUrl(this.item()));
  
  // HTML の <video> 要素を取得する
  @ViewChild('videoPlayer')
  videoRef!: ElementRef<HTMLVideoElement>;

  // 動画を先頭から再生する
  resetPlaybackPosition(): boolean {
    const video = this.videoRef.nativeElement;
    video.currentTime = 0;
    video.play();
    return true;
  }
}