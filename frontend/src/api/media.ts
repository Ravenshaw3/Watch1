import apiClient from './client'
import type {
  MediaFile,
  MediaSearchResponse,
  MediaUploadResponse,
  MediaCategoryInfo,
  MediaScanResult,
  VersionInfo,
  MediaCategory,
  Playlist,
  PlaylistCreate,
  PlaylistUpdate,
  PlaylistItemAdd,
  TVSeriesResponse,
  TVEpisodesResponse
} from '@/types/media'

export const mediaApi = {
  async getMediaFiles(params: {
    page?: number
    page_size?: number
    category?: MediaCategory
    search?: string
    sort_by?: string
    sort_order?: string
  } = {}): Promise<MediaSearchResponse> {
    const response = await apiClient.get('/media', { params })
    return response.data
  },

  async getMediaFile(id: string): Promise<MediaFile> {
    const response = await apiClient.get(`/media/${id}`)
    return response.data
  },

  async getMediaCategories(): Promise<{ categories: MediaCategoryInfo[] }> {
    const response = await apiClient.get('/media/categories')
    return response.data
  },

  async scanMediaDirectory(directory: string = '/app/media'): Promise<MediaScanResult> {
    const response = await apiClient.post('/media/scan', { directory })
    return response.data
  },

  async getVersion(): Promise<VersionInfo> {
    const response = await apiClient.get('/version')
    return response.data
  },

  async getScanInfo(): Promise<any> {
    const response = await apiClient.get('/media/scan-info')
    return response.data
  },

  async getTVSeries(): Promise<TVSeriesResponse> {
    const response = await apiClient.get('/media/tv-series')
    return response.data
  },

  async getTVSeriesEpisodes(seriesKey: string, season?: number): Promise<TVEpisodesResponse> {
    const params = season ? { season } : {}
    const response = await apiClient.get(`/media/tv-series/${seriesKey}/episodes`, { params })
    return response.data
  },

  async streamMediaFile(id: string): Promise<string> {
    const response = await apiClient.get(`/media/${id}/stream`)
    return response.data.stream_url
  },

  async uploadMediaFile(file: File): Promise<MediaUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async deleteMediaFile(id: string): Promise<void> {
    await apiClient.delete(`/media/${id}`)
  },


  // Playlist API
  async getPlaylists(): Promise<Playlist[]> {
    const response = await apiClient.get('/playlists')
    return response.data
  },

  async getPlaylist(id: string): Promise<Playlist> {
    const response = await apiClient.get(`/playlists/${id}`)
    return response.data
  },

  async createPlaylist(playlistData: PlaylistCreate): Promise<Playlist> {
    const response = await apiClient.post('/playlists', playlistData)
    return response.data
  },

  async updatePlaylist(id: string, playlistData: PlaylistUpdate): Promise<Playlist> {
    const response = await apiClient.put(`/playlists/${id}`, playlistData)
    return response.data
  },

  async deletePlaylist(id: string): Promise<void> {
    await apiClient.delete(`/playlists/${id}`)
  },

  async addPlaylistItem(playlistId: string, itemData: PlaylistItemAdd): Promise<void> {
    await apiClient.post(`/playlists/${playlistId}/items`, itemData)
  },

  async removePlaylistItem(playlistId: string, mediaId: string): Promise<void> {
    await apiClient.delete(`/playlists/${playlistId}/items/${mediaId}`)
  },

  async getPlaylistMedia(playlistId: string): Promise<{ media: MediaFile[] }> {
    const response = await apiClient.get(`/playlists/${playlistId}/media`)
    return response.data
  },
}
