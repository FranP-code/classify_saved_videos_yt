import React from 'react';
import { Badge } from './ui/badge';
import type { VideoData } from '../types/video';
import { getUniqueValues } from '../utils/search';

interface StatsOverviewProps {
  data: VideoData[];
}

export function StatsOverview({ data }: StatsOverviewProps) {
  const totalVideos = data.length;
  const totalDuration = data.reduce((sum, video) => sum + video.video_length_seconds, 0);
  const uniqueChannels = getUniqueValues(data, 'channel_name').length;
  const uniqueClassifications = getUniqueValues(data, 'classification').length;
  const uniqueLanguages = getUniqueValues(data, 'language').length;

  const formatTotalDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const stats = [
    { label: 'Total Videos', value: totalVideos.toLocaleString() },
    { label: 'Total Duration', value: formatTotalDuration(totalDuration) },
    { label: 'Channels', value: uniqueChannels },
    { label: 'Categories', value: uniqueClassifications },
    { label: 'Languages', value: uniqueLanguages },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="text-center p-4 bg-card border rounded-lg">
          <div className="text-2xl font-bold text-primary">{stat.value}</div>
          <div className="text-sm text-muted-foreground">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}