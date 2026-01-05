import Papa from 'papaparse';
import type { VideoData } from '../types/video';

export function parseCSV(csvText: string): VideoData[] {
  const result = Papa.parse<VideoData>(csvText, {
    header: true,
    skipEmptyLines: true,
    transform: (value, field) => {
      // Convert numeric fields
      if (field === 'video_length_seconds') {
        return parseInt(value) || 0;
      }
      return value;
    }
  });

  if (result.errors.length > 0) {
    console.warn('CSV parsing errors:', result.errors);
  }

  return result.data;
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}