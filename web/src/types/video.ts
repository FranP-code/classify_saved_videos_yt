export interface VideoData {
  video_title: string;
  video_url: string;
  thumbnail_url: string;
  classification: string;
  language: string;
  channel_name: string;
  channel_link: string;
  video_length_seconds: number;
  video_date: string;
  detailed_subtags: string;
  playlist_name: string;
  playlist_link: string;
  image_data: string;
  timestamp: string;
}

export interface FilterOptions {
  classification: string[];
  language: string[];
  playlist_name: string[];
}