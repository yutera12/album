export type MediaType = "video" | "photo";

type BaseMedia = {
  id: string;
  year: number;
  month: number;
  day: number;
  fileName: string;
  thumbnailFileName: string;
  aspectRatio: number;
  tag: string[];
  title: string | null;
  favorite: boolean;
};

export type Video = BaseMedia & {
  type: "video";
  totalTime: number;
};

export type Photo = BaseMedia & {
  type: "photo";
  totalTime: null;
};

export type Media = Video | Photo;