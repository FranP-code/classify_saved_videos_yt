import React, { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import type { VideoData } from '../types/video';
import { formatDuration, formatDate } from '../utils/csvParser';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface VirtualTableProps {
  data: VideoData[];
}

export function VirtualTable({ data }: VirtualTableProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  console.log(data);
  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120,
    overscan: 5,
  });

  const virtualItems = rowVirtualizer.getVirtualItems();

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Table Header */}
      <div className="bg-muted/50 border-b p-4">
        <div className="grid grid-cols-12 gap-4 text-sm font-medium text-muted-foreground">
          <div className="col-span-2">Video</div>
          <div className="col-span-2">Channel</div>
          <div className="col-span-2">Classification</div>
          <div className="col-span-2">Language</div>
          <div className="col-span-1">Duration</div>
          <div className="col-span-2">Date</div>
          <div className="col-span-1">Actions</div>
        </div>
      </div>

      {/* Virtual Container */}
      <div
        ref={parentRef}
        className="h-[600px] overflow-auto"
        style={{
          contain: 'strict',
        }}
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {virtualItems.map((virtualItem) => {
            const video = data[virtualItem.index];
            console.log(data, virtualItem, video);
            if (!video) return null;

            return (
              <div
                key={virtualItem.key}
                data-index={virtualItem.index}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${virtualItem.start}px)`,
                }}
              >
                <div className="border-b p-4 hover:bg-muted/50 transition-colors">
                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* Video Info */}
                    <div className="col-span-2 space-y-1">
                      <h3 className="font-medium text-sm leading-tight line-clamp-2">
                        {video.video_title}
                      </h3>
                      <div className="flex flex-wrap gap-1">
                        {video.detailed_subtags.split(',').slice(0, 3).map((tag, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            {tag.trim()}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Channel */}
                    <div className="col-span-2">
                      <div className="text-sm font-medium">{video.channel_name}</div>
                      <div className="text-xs text-muted-foreground">{video.playlist_name}</div>
                    </div>

                    {/* Classification */}
                    <div className="col-span-2">
                      <Badge variant="default" className="text-xs">
                        {video.classification}
                      </Badge>
                    </div>

                    {/* Language */}
                    <div className="col-span-2">
                      <Badge variant="outline" className="text-xs">
                        {video.language}
                      </Badge>
                    </div>

                    {/* Duration */}
                    <div className="col-span-1 text-sm">
                      {formatDuration(video.video_length_seconds)}
                    </div>

                    {/* Date */}
                    <div className="col-span-2 space-y-1">
                      <div className="text-sm">{formatDate(video.video_date)}</div>
                      <div className="text-xs text-muted-foreground">
                        Added: {formatDate(video.timestamp)}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="col-span-1">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(video.video_url, '_blank')}
                        className="text-xs"
                      >
                        Watch
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="bg-muted/50 border-t p-4">
        <div className="text-sm text-muted-foreground text-center">
          Showing {data.length} videos
        </div>
      </div>
    </div>
  );
}