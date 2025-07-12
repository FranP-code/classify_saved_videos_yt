import React, { useState, useEffect, useMemo } from 'react';
import { VirtualTable } from './VirtualTable';
import { SearchAndFilter } from './SearchAndFilter';
import { StatsOverview } from './StatsOverview';
import { Button } from './ui/button';
import type { VideoData } from '../types/video';
import { searchVideos, filterVideos } from '../utils/search';

interface ApiResponse {
  videos?: VideoData[];
  error?: string;
  message?: string;
}

export default function VideoClassifierApp() {
  const [data, setData] = useState<VideoData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    classification: 'all',
    language: 'all',
    playlist_name: 'all'
  });

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/videos');
        const result: ApiResponse = await response.json();

        if (!response.ok || result.error) {
          setError(result.message || result.error || 'Failed to load data');
          setData([]);
        } else {
          setData(result.videos || []);
          setError(null);
        }
      } catch (err) {
        setError('Failed to fetch video data');
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter and search data
  const filteredData = useMemo(() => {
    let result = data;
    
    // Apply filters
    result = filterVideos(result, filters);
    
    // Apply search
    result = searchVideos(result, searchTerm);
    
    return result;
  }, [data, searchTerm, filters]);

  const refreshData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/videos');
      const result: ApiResponse = await response.json();

      if (!response.ok || result.error) {
        setError(result.message || result.error || 'Failed to load data');
        setData([]);
      } else {
        setData(result.videos || []);
        setError(null);
      }
    } catch (err) {
      setError('Failed to fetch video data');
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading video data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-md text-center space-y-4">
          <div className="text-6xl">📁</div>
          <h1 className="text-2xl font-bold text-destructive">CSV File Not Found</h1>
          <p className="text-muted-foreground">
            {error}
          </p>
          <div className="bg-muted p-4 rounded-lg text-sm text-left">
            <p className="font-medium mb-2">To fix this:</p>
            <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
              <li>Make sure <code className="bg-background px-1 rounded">video_classifications.csv</code> exists in your project root</li>
              <li>Run your YouTube classifier script to generate the CSV</li>
              <li>Refresh this page</li>
            </ol>
          </div>
          <Button onClick={refreshData} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            YouTube Video Classifier
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            AI-powered video classification and management platform. Search, filter, and organize your YouTube video collection with intelligent categorization.
          </p>
        </div>

        {/* Stats Overview */}
        {data.length > 0 && (
          <StatsOverview data={data} />
        )}

        {/* Search and Filter */}
        {data.length > 0 && (
          <SearchAndFilter
            data={data}
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
            filters={filters}
            onFilterChange={setFilters}
            totalResults={data.length}
            filteredResults={filteredData.length}
          />
        )}

        {/* Results */}
        {data.length > 0 ? (
          filteredData.length > 0 ? (
            <VirtualTable data={filteredData} />
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-lg font-medium mb-2">No results found</h3>
              <p className="text-muted-foreground">
                Try adjusting your search terms or filters
              </p>
            </div>
          )
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📹</div>
            <h3 className="text-lg font-medium mb-2">No videos found</h3>
            <p className="text-muted-foreground">
              Your CSV file appears to be empty
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground border-t pt-8">
          <p>
            Powered by AI classification • {data.length} videos indexed
          </p>
          <Button
            variant="ghost"
            size="sm"
            onClick={refreshData}
            className="mt-2"
          >
            Refresh Data
          </Button>
        </div>
      </div>
    </div>
  );
}