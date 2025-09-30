<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Media Library
            </h1>
            <p class="text-gray-600 mt-1">Browse and manage your media collection</p>
          </div>
          <div class="flex gap-2">
            <button
              @click="scanMedia"
              :disabled="isScanning"
              class="btn-outline"
            >
              <span v-if="isScanning">Scanning...</span>
              <span v-else>Scan Media</span>
            </button>
            <button
              @click="showUpload = true"
              class="btn-primary"
            >
              Upload Media
            </button>
          </div>
        </div>
        
        <!-- Library Status Box -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div class="flex items-center justify-between">
            <div class="grid grid-cols-4 gap-8">
              <div class="text-center">
                <div class="text-3xl font-bold text-gray-900">{{ total }}</div>
                <div class="text-sm text-gray-600">Total Files</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">{{ safeMediaArray.length }}</div>
                <div class="text-sm text-gray-600">Showing</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-green-600">{{ enabledCategoriesCount }}</div>
                <div class="text-sm text-gray-600">Categories</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-blue-600">{{ selectedCategoryInfo?.displayName || 'All' }}</div>
                <div class="text-sm text-gray-600">Current View</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-600">Last Scan</div>
              <div class="text-sm font-medium text-gray-900">{{ lastScanTime || 'Never' }}</div>
            </div>
          </div>
        </div>
        
        <!-- Enhanced Category Manager -->
        <CategoryManager
          :categories="categoriesData"
          :selected-category="selectedCategory"
          @category-selected="handleCategorySelected"
          @categories-updated="handleCategoriesUpdated"
        />
        
        <!-- Enhanced Filters -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div class="flex flex-wrap gap-4 items-center">
            <div class="flex-1 min-w-64">
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                type="text"
                :placeholder="`Search ${selectedCategoryInfo?.displayName || 'media'}...`"
                class="input w-full"
              />
            </div>
            
            <div class="flex gap-2">
              <select
                v-model="sortBy"
                @change="applyFilters"
                class="input w-auto"
              >
                <option value="created_at">Date Added</option>
                <option value="filename">Name</option>
                <option value="file_size">Size</option>
                <option value="duration">Duration</option>
              </select>
              
              <select
                v-model="sortOrder"
                @change="applyFilters"
                class="input w-auto"
              >
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
              
              <select
                v-model="viewMode"
                @change="updateViewMode"
                class="input w-auto"
              >
                <option value="grid">Grid View</option>
                <option value="list">List View</option>
                <option value="card">Card View</option>
              </select>
              
              <select
                v-model="pageSize"
                @change="applyFilters"
                class="input w-auto"
              >
                <option value="12">12 per page</option>
                <option value="24">24 per page</option>
                <option value="36">36 per page</option>
                <option value="48">48 per page</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Scan Information -->
      <ScanInfo ref="scanInfoRef" class="mb-8" />

      <!-- Loading State -->
      <div v-if="mediaStore.isLoading && mediaStore.mediaFiles.length === 0" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading media files...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="mediaStore.mediaFiles.length === 0" class="text-center py-12">
        <FilmIcon class="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          No media files found
        </h3>
        <p class="text-gray-600 mb-6">
          Upload some media files or scan your media directory to get started.
        </p>
        <div class="flex gap-4 justify-center">
          <button @click="showUpload = true" class="btn-primary">
            Upload Media
          </button>
          <button @click="scanMedia" class="btn-outline">
            Scan Directory
          </button>
        </div>
      </div>

      <!-- Media Grid -->
      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <MediaCard
            v-for="media in safeMediaArray"
            :key="media?.id || `media-${Math.random()}`"
            :media="media"
          />
        </div>
        
        <!-- List View -->
        <div v-else-if="viewMode === 'list'" class="space-y-2">
          <div
            v-for="media in safeMediaArray"
            :key="media?.id || `media-${Math.random()}`"
            class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex items-center space-x-4 hover:shadow-md transition-shadow cursor-pointer"
            @click="navigateToPlayer(media)"
          >
            <img
              v-if="media?.id"
              :src="getPosterUrl(media.id)"
              :alt="media?.title || media?.filename"
              class="w-16 h-24 object-cover rounded"
              @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
            />
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900">{{ media?.title || media?.filename || 'Unknown' }}</h3>
              <p class="text-sm text-gray-600 capitalize">{{ media?.category || 'Unknown' }}</p>
              <p class="text-sm text-gray-500">{{ formatFileSize(media?.file_size || 0) }}</p>
            </div>
            <div class="text-right">
              <p v-if="media?.duration" class="text-sm text-gray-600">{{ formatDuration(media.duration) }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(media?.created_at) }}</p>
            </div>
          </div>
        </div>
        
        <!-- Card View -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="media in safeMediaArray"
            :key="media?.id || `media-${Math.random()}`"
            class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
            @click="navigateToPlayer(media)"
          >
            <img
              v-if="media?.id"
              :src="getPosterUrl(media.id)"
              :alt="media?.title || media?.filename"
              class="w-full h-48 object-cover"
              @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
            />
            <div class="p-4">
              <h3 class="font-semibold text-gray-900 mb-2">{{ media?.title || media?.filename || 'Unknown' }}</h3>
              <div class="flex justify-between items-center text-sm text-gray-600">
                <span class="capitalize">{{ media?.category || 'Unknown' }}</span>
                <span>{{ formatFileSize(media?.file_size || 0) }}</span>
              </div>
              <div class="flex justify-between items-center text-xs text-gray-500 mt-2">
                <span v-if="media?.duration">{{ formatDuration(media.duration) }}</span>
                <span>{{ formatDate(media?.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-center items-center mt-8 gap-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="btn-outline"
          >
            Previous
          </button>
          
          <div class="flex gap-1">
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              :class="[
                'px-3 py-1 rounded text-sm',
                page === currentPage
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
              ]"
            >
              {{ page }}
            </button>
          </div>
          
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
            class="btn-outline"
          >
            Next
          </button>
        </div>
        
        <!-- Results Info - Always show when there are results -->
        <div v-if="total > 0" class="text-center mt-4 text-sm text-gray-600">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, total) }} of {{ total }} results
        </div>
      </div>
      
      <!-- Upload Modal -->
      <div v-if="showUpload" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 class="text-lg font-medium mb-4">Upload Media File</h3>
          <input
            ref="fileInput"
            type="file"
            accept="video/*,audio/*,image/*"
            @change="handleFileUpload"
            class="input mb-4"
          />
          <div class="flex gap-2 justify-end">
            <button @click="showUpload = false" class="btn-outline">Cancel</button>
            <button @click="uploadFile" :disabled="!selectedFile" class="btn-primary">
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMediaStore } from '@/stores/media'
import { mediaApi } from '@/api/media'
import MediaCard from '@/components/MediaCardNew.vue'
import ScanInfo from '@/components/ScanInfo.vue'
import CategoryManager from '@/components/CategoryManager.vue'
import { FilmIcon } from '@heroicons/vue/24/outline'
import type { MediaCategory, MediaCategoryInfo } from '@/types/media'

const mediaStore = useMediaStore()

// State
const categories = ref<MediaCategoryInfo[]>([])
const selectedCategory = ref<string>('movies') // Default to movies
const searchQuery = ref('')
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = ref(24) // Updated default
const total = ref(0)
const totalPages = ref(1)
const isScanning = ref(false)
const showUpload = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const lastScanTime = ref<string>('')
const viewMode = ref<'grid' | 'list' | 'card'>('grid')

// Category management state
const categoryManagement = ref({
  enabled: true,
  categories: {} as Record<string, number>
})

// Computed
const safeMediaArray = computed(() => {
  return Array.isArray(mediaStore.mediaFiles) ? mediaStore.mediaFiles : []
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// New computed properties for enhanced category system
const categoriesData = computed(() => {
  return categoryManagement.value.categories
})

const enabledCategoriesCount = computed(() => {
  return Object.keys(categoryManagement.value.categories).length
})

const selectedCategoryInfo = computed(() => {
  // Mock category info based on selected category
  const categoryMap: Record<string, any> = {
    'movies': { displayName: 'Movies', description: 'Feature films and cinema' },
    'tv_shows': { displayName: 'TV Shows', description: 'Television series and episodes' },
    'kids': { displayName: 'Kids', description: 'Family-friendly content' },
    'music': { displayName: 'Music', description: 'Audio files and music' },
    'videos': { displayName: 'Videos', description: 'General video content' },
    'all': { displayName: 'All Media', description: 'All media types' }
  }
  
  return categoryMap[selectedCategory.value] || categoryMap['all']
})

// Debounced search
let searchTimeout: NodeJS.Timeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 300)
}

// Methods
async function loadCategories() {
  try {
    const response = await mediaApi.getMediaCategories()
    // Ensure we always have a valid array
    if (Array.isArray(response.categories)) {
      categories.value = response.categories
    } else if (Array.isArray(response)) {
      categories.value = response
    } else {
      console.warn('Unexpected categories response format:', response)
      categories.value = []
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
    categories.value = []
  }
}

async function loadMedia() {
  try {
    const response = await mediaApi.getMediaFiles({
      page: currentPage.value,
      page_size: pageSize.value,
      category: selectedCategory.value as MediaCategory,
      search: searchQuery.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    })
    
    // Handle different response formats safely
    if (Array.isArray(response.items)) {
      mediaStore.mediaFiles = response.items
    } else if (Array.isArray(response.media)) {
      mediaStore.mediaFiles = response.media
    } else if (Array.isArray(response)) {
      mediaStore.mediaFiles = response
    } else {
      console.warn('Unexpected media response format:', response)
      mediaStore.mediaFiles = []
    }
    
    total.value = response.total || 0
    totalPages.value = Math.ceil((response.total || 0) / pageSize.value)
  } catch (error) {
    console.error('Failed to load media:', error)
    mediaStore.mediaFiles = []
    total.value = 0
    totalPages.value = 1
  }
}

// Removed selectCategory function - now handled by CategoryManager component

function applyFilters() {
  currentPage.value = 1
  loadMedia()
}

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadMedia()
  }
}

async function scanMedia() {
  isScanning.value = true
  try {
    const result = await mediaApi.scanMediaDirectory()
    console.log('Scan result:', result)
    await loadMedia()
    await loadCategories()
  } catch (error) {
    console.error('Failed to scan media:', error)
  } finally {
    isScanning.value = false
  }
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

async function uploadFile() {
  if (!selectedFile.value) return
  
  try {
    await mediaApi.uploadMediaFile(selectedFile.value)
    showUpload.value = false
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    await loadMedia()
    await loadCategories()
  } catch (error) {
    console.error('Failed to upload file:', error)
  }
}

// Enhanced category management methods
function handleCategorySelected(categoryId: string) {
  selectedCategory.value = categoryId
  currentPage.value = 1
  applyFilters()
}

function handleCategoriesUpdated(updatedCategories: any[]) {
  console.log('Categories updated:', updatedCategories)
  // Handle category configuration updates
}

function updateViewMode() {
  // Save view mode preference
  localStorage.setItem('watch1-view-mode', viewMode.value)
  // Trigger re-render if needed
}

// Update category data when categories are loaded
function updateCategoryManagement() {
  if (categories.value.length > 0) {
    const categoryData: Record<string, number> = {}
    categories.value.forEach(cat => {
      if (cat?.name && typeof cat.count === 'number') {
        categoryData[cat.name] = cat.count
      }
    })
    categoryManagement.value.categories = categoryData
  }
}

// Utility functions for different view modes
function navigateToPlayer(media: any) {
  if (media?.id) {
    // Use router to navigate to player
    window.location.href = `/player/${media.id}`
  }
}

function getPosterUrl(mediaId: string): string {
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${mediaId}/poster?token=${token}`
}

function formatFileSize(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDuration(seconds: number): string {
  if (!seconds || typeof seconds !== 'number') return ''
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function formatDate(dateString: string | null): string {
  if (!dateString) return ''
  
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return ''
  }
}

// Lifecycle
onMounted(async () => {
  // Load saved view mode preference
  const savedViewMode = localStorage.getItem('watch1-view-mode')
  if (savedViewMode && ['grid', 'list', 'card'].includes(savedViewMode)) {
    viewMode.value = savedViewMode as 'grid' | 'list' | 'card'
  }
  
  await loadCategories()
  await loadMedia()
  updateCategoryManagement()
})

// Page and category changes handled in component methods
</script>
