export interface MediaFile {
  id: string
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  mime_type: string
  category: MediaCategory
  duration?: number
  width?: number
  height?: number
  bitrate?: number
  codec?: string
  container_format?: string
  thumbnail_path?: string
  poster_path?: string
  artwork?: string // Base64 encoded artwork
  metadata?: Record<string, any>
  created_at: string
  uploaded_by: string
  last_accessed?: string
}

export enum MediaCategory {
  MOVIES = "movies",
  TV_SHOWS = "tv_shows",
  KIDS = "kids",
  MUSIC_VIDEOS = "music_videos",
  AUDIO = "audio",
  IMAGES = "images",
  OTHER = "other"
}

export interface MediaMetadata {
  id: number
  media_file_id: number
  title?: string
  description?: string
  genre?: string
  year?: number
  director?: string
  cast?: string[]
  rating?: string
  language?: string
  country?: string
  studio?: string
  tags?: string[]
  imdb_id?: string
  tmdb_id?: string
  created_at: string
  updated_at?: string
}

export interface MediaSearchParams {
  query?: string
  media_type?: 'video' | 'audio' | 'image'
  genre?: string
  year?: number
  tags?: string[]
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  page: number
  page_size: number
}

export interface MediaSearchResponse {
  media: MediaFile[]
  total: number
  page: number
  page_size: number
  categories: Record<string, number>
}

export interface MediaCategoryInfo {
  name: string
  count: number
  display_name: string
}

export interface MediaScanResult {
  scanned_files: number
  new_files: number
  updated_files: number
  errors: string[]
  categories: Record<string, number>
}

export interface VersionInfo {
  version: string
  build_date: string
  features: string[]
}

export interface MediaUploadResponse {
  file_id: number
  filename: string
  status: string
  message: string
}

export interface TVSeries {
  series_name: string
  seasons: Record<number, TVEpisode[]>
}

export interface TVEpisode {
  id: string
  filename: string
  episode: number
  file_path: string
  duration?: number
  artwork?: string
}

export interface TVSeriesResponse {
  series: TVSeries[]
}

export interface TVEpisodesResponse {
  episodes: TVEpisode[]
}

export interface PlaylistItem {
  media_id: string
  position: number
  added_at: string
}

export interface Playlist {
  id: string
  name: string
  description?: string
  items: PlaylistItem[]
  created_by: string
  created_at: string
  updated_at: string
  is_public: boolean
}

export interface PlaylistCreate {
  name: string
  description?: string
  is_public?: boolean
}

export interface PlaylistUpdate {
  name?: string
  description?: string
  is_public?: boolean
}

export interface PlaylistItemAdd {
  media_id: string
  position?: number
}

export interface SubtitleInfo {
  src: string
  label: string
  language: string
  default?: boolean
}
