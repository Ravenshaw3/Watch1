export interface MediaFile {
  id: string
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  mime_type: string
  duration?: number
  width?: number
  height?: number
  created_at: string
  uploaded_by: string
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
