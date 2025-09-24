import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MediaFile, MediaSearchParams, MediaSearchResponse } from '@/types/media'
import { mediaApi } from '@/api/media'

export const useMediaStore = defineStore('media', () => {
  // State
  const mediaFiles = ref<MediaFile[]>([])
  const currentMedia = ref<MediaFile | null>(null)
  const searchResults = ref<MediaSearchResponse | null>(null)
  const isLoading = ref(false)
  const currentPage = ref(1)
  const totalPages = ref(1)
  const searchQuery = ref('')
  const filters = ref<Partial<MediaSearchParams>>({})

  // Getters with safe array access
  const videoFiles = computed(() => {
    const files = mediaFiles.value || []
    return files.filter(file => 
      file?.mime_type?.startsWith('video/') || 
      file?.category === 'movies' || 
      file?.category === 'tv_shows' ||
      (file?.filename && /\.(mp4|mkv|avi|mov|wmv|flv|webm)$/i.test(file.filename))
    )
  })
  
  const audioFiles = computed(() => {
    const files = mediaFiles.value || []
    return files.filter(file => 
      file?.mime_type?.startsWith('audio/') ||
      file?.category === 'music_videos' ||
      (file?.filename && /\.(mp3|wav|flac|aac|ogg|m4a)$/i.test(file.filename))
    )
  })
  
  const imageFiles = computed(() => {
    const files = mediaFiles.value || []
    return files.filter(file => 
      file?.mime_type?.startsWith('image/') ||
      (file?.filename && /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/i.test(file.filename))
    )
  })

  const recentFiles = computed(() => {
    const files = mediaFiles.value || []
    return [...files]
      .sort((a, b) => {
        const dateA = a?.created_at ? new Date(a.created_at).getTime() : 0
        const dateB = b?.created_at ? new Date(b.created_at).getTime() : 0
        return dateB - dateA
      })
      .slice(0, 20)
  })

  // Actions
  async function fetchMediaFiles(params: Partial<MediaSearchParams> = {}) {
    isLoading.value = true
    try {
      const response = await mediaApi.getMediaFiles({
        page: currentPage.value,
        page_size: 20,
        ...filters.value,
        ...params
      })
      
      const items = response.items || response.media || []
      if (params.page === 1 || !params.page) {
        mediaFiles.value = Array.isArray(items) ? items : []
      } else {
        const currentFiles = mediaFiles.value || []
        mediaFiles.value = [...currentFiles, ...(Array.isArray(items) ? items : [])]
      }
      
      searchResults.value = response
      totalPages.value = Math.ceil(response.total / response.page_size)
      currentPage.value = response.page
      
      return response
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMediaFile(id: number) {
    try {
      const response = await mediaApi.getMediaFile(id.toString())
      currentMedia.value = response
      return response
    } catch (error) {
      throw error
    }
  }

  async function searchMedia(query: string, params: Partial<MediaSearchParams> = {}) {
    searchQuery.value = query
    isLoading.value = true
    
    try {
      const response = await mediaApi.getMediaFiles({
        query,
        page: 1,
        page_size: 20,
        ...params
      })
      
      const items = response.items || response.media || []
      mediaFiles.value = Array.isArray(items) ? items : []
      searchResults.value = response
      totalPages.value = Math.ceil(response.total / response.page_size)
      currentPage.value = 1
      
      return response
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function uploadMediaFile(file: File) {
    isLoading.value = true
    try {
      const response = await mediaApi.uploadMediaFile(file)
      // Refresh the media list
      await fetchMediaFiles({ page: 1 })
      return response
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function deleteMediaFile(id: number) {
    try {
      await mediaApi.deleteMediaFile(id.toString())
      // Remove from local state
      const currentFiles = mediaFiles.value || []
      mediaFiles.value = currentFiles.filter(file => file?.id !== id.toString())
      if (currentMedia.value?.id === id.toString()) {
        currentMedia.value = null
      }
    } catch (error) {
      throw error
    }
  }

  function setFilters(newFilters: Partial<MediaSearchParams>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function clearFilters() {
    filters.value = {}
    searchQuery.value = ''
  }

  function loadMore() {
    if (currentPage.value < totalPages.value && !isLoading.value) {
      currentPage.value += 1
      fetchMediaFiles({ page: currentPage.value })
    }
  }

  return {
    // State
    mediaFiles,
    currentMedia,
    searchResults,
    isLoading,
    currentPage,
    totalPages,
    searchQuery,
    filters,
    
    // Getters
    videoFiles,
    audioFiles,
    imageFiles,
    recentFiles,
    
    // Actions
    fetchMediaFiles,
    fetchMediaFile,
    searchMedia,
    uploadMediaFile,
    deleteMediaFile,
    setFilters,
    clearFilters,
    loadMore
  }
})
