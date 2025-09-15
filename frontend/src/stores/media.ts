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

  // Getters
  const videoFiles = computed(() => 
    mediaFiles.value.filter(file => file.media_type === 'video')
  )
  
  const audioFiles = computed(() => 
    mediaFiles.value.filter(file => file.media_type === 'audio')
  )
  
  const imageFiles = computed(() => 
    mediaFiles.value.filter(file => file.media_type === 'image')
  )

  const recentFiles = computed(() => 
    [...mediaFiles.value]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 20)
  )

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
      
      if (params.page === 1 || !params.page) {
        mediaFiles.value = response.items
      } else {
        mediaFiles.value.push(...response.items)
      }
      
      searchResults.value = response
      totalPages.value = response.total_pages
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
      const response = await mediaApi.getMediaFile(id)
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
      const response = await mediaApi.searchMedia({
        query,
        page: 1,
        page_size: 20,
        ...params
      })
      
      mediaFiles.value = response.items
      searchResults.value = response
      totalPages.value = response.total_pages
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
      await mediaApi.deleteMediaFile(id)
      // Remove from local state
      mediaFiles.value = mediaFiles.value.filter(file => file.id !== id)
      if (currentMedia.value?.id === id) {
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
