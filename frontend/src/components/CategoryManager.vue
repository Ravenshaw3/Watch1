<template>
  <div class="category-manager">
    <!-- Category Configuration Panel -->
    <div v-if="showConfig" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">Category Management</h2>
          <button @click="showConfig = false" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Category Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-card bg-gray-50 rounded-lg p-4 border-2 transition-all"
            :class="category.enabled ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <component :is="category.icon" class="h-8 w-8" :class="category.color" />
                <div>
                  <h3 class="font-semibold text-gray-900">{{ category.displayName }}</h3>
                  <p class="text-sm text-gray-600">{{ category.description }}</p>
                </div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  v-model="category.enabled"
                  @change="updateCategory(category)"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <!-- Category Stats -->
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div class="text-center">
                <div class="font-bold text-lg text-gray-900">{{ category.fileCount || 0 }}</div>
                <div class="text-gray-600">Files</div>
              </div>
              <div class="text-center">
                <div class="font-bold text-lg text-gray-900">{{ category.mediaType }}</div>
                <div class="text-gray-600">Type</div>
              </div>
            </div>

            <!-- Player Type Selection -->
            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Player Type</label>
              <select
                v-model="category.playerType"
                @change="updateCategory(category)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="video">Video Player</option>
                <option value="audio">Audio Player</option>
                <option value="image">Image Viewer</option>
                <option value="auto">Auto Detect</option>
              </select>
            </div>

            <!-- Category Settings -->
            <div class="mt-4 space-y-2">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="category.showInTabs"
                  @change="updateCategory(category)"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Show in Library Tabs</span>
              </label>
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="category.allowUpload"
                  @change="updateCategory(category)"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Allow File Upload</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-between items-center mt-8">
          <button
            @click="addCustomCategory"
            class="btn-outline"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            Add Custom Category
          </button>
          <div class="space-x-3">
            <button @click="resetToDefaults" class="btn-outline">
              Reset to Defaults
            </button>
            <button @click="saveConfiguration" class="btn-primary">
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Tabs for Library -->
    <div class="category-tabs">
      <div class="flex flex-wrap gap-2 mb-6">
        <button
          v-for="category in enabledCategories"
          :key="category.id"
          @click="selectCategory(category.id)"
          :class="[
            'category-tab flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            selectedCategory === category.id
              ? 'bg-primary-600 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300 hover:border-gray-400'
          ]"
        >
          <component :is="category.icon" class="h-5 w-5" />
          <span>{{ category.displayName }}</span>
          <span class="bg-black bg-opacity-20 text-xs px-2 py-1 rounded-full">
            {{ category.fileCount || 0 }}
          </span>
        </button>
        
        <!-- All Categories Tab -->
        <button
          @click="selectCategory('all')"
          :class="[
            'category-tab flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            selectedCategory === 'all'
              ? 'bg-gray-800 text-white shadow-lg'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300 hover:border-gray-400'
          ]"
        >
          <ViewColumnsIcon class="h-5 w-5" />
          <span>All Media</span>
          <span class="bg-black bg-opacity-20 text-xs px-2 py-1 rounded-full">
            {{ totalFiles }}
          </span>
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="flex justify-between items-center mb-4">
      <div class="flex items-center space-x-4">
        <span class="text-sm text-gray-600">
          Showing {{ selectedCategoryInfo?.displayName || 'All Media' }}
        </span>
        <span v-if="selectedCategoryInfo" class="text-xs text-gray-500">
          {{ selectedCategoryInfo.description }}
        </span>
      </div>
      <button
        @click="showConfig = true"
        class="btn-outline text-sm"
      >
        <CogIcon class="h-4 w-4 mr-2" />
        Manage Categories
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  XMarkIcon,
  PlusIcon,
  CogIcon,
  ViewColumnsIcon,
  FilmIcon,
  MusicalNoteIcon,
  PhotoIcon,
  VideoCameraIcon,
  HeartIcon,
  AcademicCapIcon,
  TvIcon
} from '@heroicons/vue/24/outline'

interface MediaCategory {
  id: string
  displayName: string
  description: string
  icon: any
  color: string
  mediaType: 'video' | 'audio' | 'image' | 'mixed'
  playerType: 'video' | 'audio' | 'image' | 'auto'
  enabled: boolean
  showInTabs: boolean
  allowUpload: boolean
  fileCount?: number
  sortOrder: number
}

interface Props {
  categories?: Record<string, number>
  selectedCategory?: string
}

interface Emits {
  (e: 'category-selected', category: string): void
  (e: 'categories-updated', categories: MediaCategory[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const showConfig = ref(false)
const selectedCategory = ref(props.selectedCategory || 'movies')

// Default categories configuration
const defaultCategories: MediaCategory[] = [
  {
    id: 'movies',
    displayName: 'Movies',
    description: 'Feature films and cinema',
    icon: FilmIcon,
    color: 'text-blue-600',
    mediaType: 'video',
    playerType: 'video',
    enabled: true,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 1
  },
  {
    id: 'tv_shows',
    displayName: 'TV Shows',
    description: 'Television series and episodes',
    icon: TvIcon,
    color: 'text-purple-600',
    mediaType: 'video',
    playerType: 'video',
    enabled: true,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 2
  },
  {
    id: 'kids',
    displayName: 'Kids',
    description: 'Family-friendly content',
    icon: HeartIcon,
    color: 'text-pink-600',
    mediaType: 'video',
    playerType: 'video',
    enabled: true,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 3
  },
  {
    id: 'music',
    displayName: 'Music',
    description: 'Audio files and music',
    icon: MusicalNoteIcon,
    color: 'text-green-600',
    mediaType: 'audio',
    playerType: 'audio',
    enabled: true,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 4
  },
  {
    id: 'videos',
    displayName: 'Videos',
    description: 'General video content',
    icon: VideoCameraIcon,
    color: 'text-orange-600',
    mediaType: 'video',
    playerType: 'video',
    enabled: true,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 5
  },
  {
    id: 'documentaries',
    displayName: 'Documentaries',
    description: 'Educational and documentary content',
    icon: AcademicCapIcon,
    color: 'text-indigo-600',
    mediaType: 'video',
    playerType: 'video',
    enabled: false,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 6
  },
  {
    id: 'photos',
    displayName: 'Photos',
    description: 'Images and photo galleries',
    icon: PhotoIcon,
    color: 'text-yellow-600',
    mediaType: 'image',
    playerType: 'image',
    enabled: false,
    showInTabs: true,
    allowUpload: true,
    sortOrder: 7
  }
]

const categories = ref<MediaCategory[]>([...defaultCategories])

// Computed properties
const enabledCategories = computed(() => {
  return categories.value
    .filter(cat => cat.enabled && cat.showInTabs)
    .sort((a, b) => a.sortOrder - b.sortOrder)
})

const selectedCategoryInfo = computed(() => {
  return categories.value.find(cat => cat.id === selectedCategory.value)
})

const totalFiles = computed(() => {
  if (!props.categories) return 0
  return Object.values(props.categories).reduce((sum, count) => sum + count, 0)
})

// Methods
function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
  emit('category-selected', categoryId)
}

function updateCategory(_category: MediaCategory) {
  // Emit updated categories
  emit('categories-updated', categories.value)
  
  // Save to localStorage
  localStorage.setItem('watch1-categories', JSON.stringify(categories.value))
}

function addCustomCategory() {
  const newCategory: MediaCategory = {
    id: `custom-${Date.now()}`,
    displayName: 'New Category',
    description: 'Custom category',
    icon: FilmIcon,
    color: 'text-gray-600',
    mediaType: 'mixed',
    playerType: 'auto',
    enabled: true,
    showInTabs: true,
    allowUpload: true,
    sortOrder: categories.value.length + 1
  }
  
  categories.value.push(newCategory)
  updateCategory(newCategory)
}

function resetToDefaults() {
  categories.value = [...defaultCategories]
  updateCategory(categories.value[0])
}

function saveConfiguration() {
  localStorage.setItem('watch1-categories', JSON.stringify(categories.value))
  showConfig.value = false
  
  // Emit updated categories
  emit('categories-updated', categories.value)
}

function loadConfiguration() {
  const saved = localStorage.getItem('watch1-categories')
  if (saved) {
    try {
      const savedCategories = JSON.parse(saved)
      // Merge with defaults to ensure we have all properties
      categories.value = defaultCategories.map(defaultCat => {
        const savedCat = savedCategories.find((s: MediaCategory) => s.id === defaultCat.id)
        return savedCat ? { ...defaultCat, ...savedCat } : defaultCat
      })
    } catch (error) {
      console.error('Failed to load category configuration:', error)
      categories.value = [...defaultCategories]
    }
  }
}

// Update file counts when props change
function updateFileCounts() {
  if (props.categories) {
    categories.value.forEach(category => {
      category.fileCount = props.categories?.[category.id] || 0
    })
  }
}

// Lifecycle
onMounted(() => {
  loadConfiguration()
  updateFileCounts()
  
  // Set default category to movies if not specified
  if (!props.selectedCategory) {
    selectCategory('movies')
  }
})

// Category changes handled in onMounted
</script>

<style scoped>
.category-card {
  transition: all 0.2s ease-in-out;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.category-tab {
  transition: all 0.2s ease-in-out;
}

.category-tab:hover {
  transform: translateY(-1px);
}

.btn-primary {
  @apply bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors;
}
</style>
