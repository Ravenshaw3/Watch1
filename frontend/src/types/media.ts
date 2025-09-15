export interface MediaFile {
  id: number
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  file_hash: string
  mime_type: string
  media_type: 'video' | 'audio' | 'image'
  duration?: number
  width?: number
  height?: number
  bitrate?: number
  codec?: string
  container_format?: string
  thumbnail_path?: string
  poster_path?: string
  is_processed: boolean
  is_available: boolean
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
  last_accessed?: string
  metadata?: MediaMetadata
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
  items: MediaFile[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface MediaUploadResponse {
  file_id: number
  filename: string
  status: string
  message: string
}

export interface Playlist {
  id: number
  name: string
  description?: string
  owner_id: number
  is_public: boolean
  is_smart: boolean
  smart_filters?: Record<string, any>
  created_at: string
  updated_at?: string
  items: PlaylistItem[]
}

export interface PlaylistItem {
  id: number
  playlist_id: number
  media_file_id: number
  position: number
  added_at: string
  media_file?: MediaFile
}

export interface PlaylistCreate {
  name: string
  description?: string
  is_public?: boolean
  is_smart?: boolean
  smart_filters?: Record<string, any>
}

export interface PlaylistUpdate {
  name?: string
  description?: string
  is_public?: boolean
  is_smart?: boolean
  smart_filters?: Record<string, any>
}
