import apiClient from './client'
import type { 
  MediaFile, 
  MediaSearchParams, 
  MediaSearchResponse, 
  MediaUploadResponse,
  Playlist,
  PlaylistCreate,
  PlaylistUpdate
} from '@/types/media'

export const mediaApi = {
  async getMediaFiles(params: Partial<MediaSearchParams> = {}): Promise<MediaSearchResponse> {
    const response = await apiClient.get('/media', { params })
    return response.data
  },

  async getMediaFile(id: number): Promise<MediaFile> {
    const response = await apiClient.get(`/media/${id}`)
    return response.data
  },

  async searchMedia(params: MediaSearchParams): Promise<MediaSearchResponse> {
    const response = await apiClient.get('/media', { params })
    return response.data
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

  async deleteMediaFile(id: number): Promise<void> {
    await apiClient.delete(`/media/${id}`)
  },

  async streamMediaFile(id: number): Promise<string> {
    return `${apiClient.defaults.baseURL}/media/${id}/stream`
  },

  // Playlist API
  async getPlaylists(): Promise<Playlist[]> {
    const response = await apiClient.get('/playlists')
    return response.data
  },

  async getPlaylist(id: number): Promise<Playlist> {
    const response = await apiClient.get(`/playlists/${id}`)
    return response.data
  },

  async createPlaylist(playlistData: PlaylistCreate): Promise<Playlist> {
    const response = await apiClient.post('/playlists', playlistData)
    return response.data
  },

  async updatePlaylist(id: number, playlistData: PlaylistUpdate): Promise<Playlist> {
    const response = await apiClient.put(`/playlists/${id}`, playlistData)
    return response.data
  },

  async deletePlaylist(id: number): Promise<void> {
    await apiClient.delete(`/playlists/${id}`)
  },
}
