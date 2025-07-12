import React, { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import type { VideoData } from '../types/video';
import { formatDuration, formatDate } from '../utils/csvParser';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tooltip } from './ui/tooltip';

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
      <div className="bg-muted/50 border-b">
        <div className="grid grid-cols-12 gap-3 px-4 py-3 text-sm font-medium text-muted-foreground">
          <div className="col-span-3 flex items-center">Video</div>
          <div className="col-span-2 flex items-center">Channel</div>
          <div className="col-span-2 flex items-center">Classification</div>
          <div className="col-span-1 flex items-center">Language</div>
          <div className="col-span-1 flex items-center">Duration</div>
          <div className="col-span-2 flex items-center">Date</div>
          <div className="col-span-1 flex items-center">Actions</div>
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
                <div className="border-b hover:bg-muted/50 transition-colors">
                  <div className="grid grid-cols-12 gap-3 px-4 py-3 items-center min-h-[80px]">
                    {/* Video Info */}
                    <div className="col-span-3 space-y-2 min-w-0">
                      <Tooltip content={video.video_title}>
                        <h3 className="font-medium text-sm leading-tight truncate">
                          {video.video_title}
                        </h3>
                      </Tooltip>
                      <div className="flex flex-wrap gap-1">
                        {video.detailed_subtags.split(',').slice(0, 2).map((tag, i) => (
                          <Tooltip key={i} content={tag.trim()}>
                            <Badge variant="secondary" className="text-xs max-w-20 truncate">
                              {tag.trim()}
                            </Badge>
                          </Tooltip>
                        ))}
                        {video.detailed_subtags.split(',').length > 2 && (
                          <Tooltip content={`+${video.detailed_subtags.split(',').length - 2} more tags`}>
                            <Badge variant="outline" className="text-xs">
                              +{video.detailed_subtags.split(',').length - 2}
                            </Badge>
                          </Tooltip>
                        )}
                      </div>
                    </div>

                    {/* Channel */}
                    <div className="col-span-2 min-w-0">
                      <Tooltip content={video.channel_name}>
                        <div className="text-sm font-medium truncate">{video.channel_name}</div>
                      </Tooltip>
                      <Tooltip content={video.playlist_name}>
                        <div className="text-xs text-muted-foreground truncate">{video.playlist_name}</div>
                      </Tooltip>
                    </div>

                    {/* Classification */}
                    <div className="col-span-2 min-w-0">
                      <Badge variant="default" className="text-xs truncate max-w-full">
                        {video.classification}
                      </Badge>
                    </div>

                    {/* Language */}
                    <div className="col-span-1 min-w-0">
                      <Badge variant="outline" className="text-xs truncate max-w-full">
                        {video.language}
                      </Badge>
                    </div>

                    {/* Duration */}
                    <div className="col-span-1 text-sm font-mono">
                      {formatDuration(video.video_length_seconds)}
                    </div>

                    {/* Date */}
                    <div className="col-span-2 space-y-1 min-w-0">
                      <div className="text-sm">{formatDate(video.video_date)}</div>
                      <div className="text-xs text-muted-foreground truncate">
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
      <div className="bg-muted/50 border-t px-4 py-3">
        <div className="text-sm text-muted-foreground text-center">
          Showing {data.length} videos
        </div>
      </div>
    </div>
  );
}