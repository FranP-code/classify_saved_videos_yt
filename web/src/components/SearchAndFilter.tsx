import React from 'react';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import type { VideoData } from '../types/video';
import { getUniqueValues } from '../utils/search';

interface SearchAndFilterProps {
  data: VideoData[];
  searchTerm: string;
  onSearchChange: (term: string) => void;
  filters: {
    classification: string;
    language: string;
    playlist_name: string;
  };
  onFilterChange: (filters: any) => void;
  totalResults: number;
  filteredResults: number;
}

export function SearchAndFilter({
  data,
  searchTerm,
  onSearchChange,
  filters,
  onFilterChange,
  totalResults,
  filteredResults
}: SearchAndFilterProps) {
  const classifications = getUniqueValues(data, 'classification');
  const languages = getUniqueValues(data, 'language');
  const playlists = getUniqueValues(data, 'playlist_name');

  const clearFilters = () => {
    onSearchChange('');
    onFilterChange({
      classification: 'all',
      language: 'all',
      playlist_name: 'all'
    });
  };

  const activeFiltersCount = Object.values(filters).filter(value => value !== 'all').length + (searchTerm ? 1 : 0);

  return (
    <div className="space-y-4 p-6 bg-card border rounded-lg">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-lg font-semibold">Search & Filter</h2>
          <p className="text-sm text-muted-foreground">
            {filteredResults} of {totalResults} videos
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} active
              </Badge>
            )}
          </p>
        </div>
        {activeFiltersCount > 0 && (
          <Button variant="outline" size="sm" onClick={clearFilters}>
            Clear All
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Search</label>
          <Input
            placeholder="Search videos, channels, tags..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        {/* Classification Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Classification</label>
          <Select
            value={filters.classification}
            onChange={(e) => onFilterChange({ ...filters, classification: e.target.value })}
          >
            <option value="all">All Classifications</option>
            {classifications.map((classification) => (
              <option key={classification} value={classification}>
                {classification}
              </option>
            ))}
          </Select>
        </div>

        {/* Language Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Language</label>
          <Select
            value={filters.language}
            onChange={(e) => onFilterChange({ ...filters, language: e.target.value })}
          >
            <option value="all">All Languages</option>
            {languages.map((language) => (
              <option key={language} value={language}>
                {language}
              </option>
            ))}
          </Select>
        </div>

        {/* Playlist Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Playlist</label>
          <Select
            value={filters.playlist_name}
            onChange={(e) => onFilterChange({ ...filters, playlist_name: e.target.value })}
          >
            <option value="all">All Playlists</option>
            {playlists.map((playlist) => (
              <option key={playlist} value={playlist}>
                {playlist}
              </option>
            ))}
          </Select>
        </div>
      </div>
    </div>
  );
}