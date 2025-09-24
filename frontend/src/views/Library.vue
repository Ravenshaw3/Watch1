<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex justify-between items-center mb-4">
          <h1 class="text-3xl font-bold text-gray-900">
            Media Library
          </h1>
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
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-6">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ total }}</div>
                <div class="text-sm text-gray-600">Total Files</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-primary-600">{{ safeMediaArray.length }}</div>
                <div class="text-sm text-gray-600">Showing</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ safeCategoriesArray.length }}</div>
                <div class="text-sm text-gray-600">Categories</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-600">Last Scan</div>
              <div class="text-sm font-medium text-gray-900">{{ lastScanTime || 'Never' }}</div>
            </div>
          </div>
        </div>
        
        <!-- Category Tabs -->
        <div class="flex flex-wrap gap-2 mb-6">
          <button
            v-for="category in safeCategoriesArray"
            :key="category?.name || `category-${Math.random()}`"
            @click="selectCategory(category?.name)"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              selectedCategory === category?.name
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            ]"
          >
            {{ category?.display_name || 'Unknown' }} ({{ category?.count || 0 }})
          </button>
        </div>
        
        <!-- Filters -->
        <div class="flex flex-wrap gap-4 mb-6">
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Search media..."
            class="input w-64"
          />
          
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
        <div class="media-grid">
          <MediaCard
            v-for="media in safeMediaArray"
            :key="media?.id || `media-${Math.random()}`"
            :media="media"
          />
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
import { ref, onMounted, computed, watch } from 'vue'
import { useMediaStore } from '@/stores/media'
import { mediaApi } from '@/api/media'
import MediaCard from '@/components/MediaCardNew.vue'
import ScanInfo from '@/components/ScanInfo.vue'
import { FilmIcon } from '@heroicons/vue/24/outline'
import type { MediaCategory, MediaCategoryInfo } from '@/types/media'

const mediaStore = useMediaStore()

// State
const categories = ref<MediaCategoryInfo[]>([])
const selectedCategory = ref<string>('')
const searchQuery = ref('')
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(1)
const isScanning = ref(false)
const showUpload = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const lastScanTime = ref<string>('')

// Computed
const safeCategoriesArray = computed(() => {
  return Array.isArray(categories.value) ? categories.value : []
})

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

function selectCategory(category?: string) {
  if (!category) {
    console.warn('selectCategory called with invalid category:', category)
    return
  }
  selectedCategory.value = selectedCategory.value === category ? '' : category
  currentPage.value = 1
  applyFilters()
}

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

// Removed viewMedia function - MediaCard now handles navigation internally

// Lifecycle
onMounted(async () => {
  await loadCategories()
  await loadMedia()
})

// Watch for page changes
watch(currentPage, () => {
  loadMedia()
})
</script>
