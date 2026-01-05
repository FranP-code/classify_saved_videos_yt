import type { VideoData } from '../types/video';

export function searchVideos(videos: VideoData[], searchTerm: string): VideoData[] {
  if (!searchTerm.trim()) return videos;

  const term = searchTerm.toLowerCase();
  
  return videos.filter(video => {
    const searchableFields = [
      video.video_title,
      video.channel_name,
      video.detailed_subtags,
      video.classification,
      video.language,
      video.playlist_name,
      video.video_length_seconds.toString(),
      formatDateForSearch(video.video_date),
      formatDateForSearch(video.timestamp)
    ];

    return searchableFields.some(field => 
      field && field.toLowerCase().includes(term)
    );
  });
}

function formatDateForSearch(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US');
  } catch {
    return dateString;
  }
}

export function filterVideos(
  videos: VideoData[], 
  filters: { classification?: string; language?: string; playlist_name?: string }
): VideoData[] {
  return videos.filter(video => {
    if (filters.classification && filters.classification !== 'all' && video.classification !== filters.classification) {
      return false;
    }
    if (filters.language && filters.language !== 'all' && video.language !== filters.language) {
      return false;
    }
    if (filters.playlist_name && filters.playlist_name !== 'all' && video.playlist_name !== filters.playlist_name) {
      return false;
    }
    return true;
  });
}

export function getUniqueValues(videos: VideoData[], field: keyof VideoData): string[] {
  const values = videos.map(video => video[field] as string).filter(Boolean);
  return [...new Set(values)].sort();
}