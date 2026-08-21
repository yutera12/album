import { Media } from "@/models/media";
import { environment } from "@/../environment";

export function mediaUrl(media: Media): string {
  return `${environment.apiUrl}/media/${media.type}/${encodeURIComponent(media.id)}`;
}