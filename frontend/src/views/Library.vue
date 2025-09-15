<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Media Library
        </h1>
        
        <!-- Filters -->
        <div class="flex flex-wrap gap-4 mb-6">
          <select
            v-model="selectedMediaType"
            @change="applyFilters"
            class="input w-auto"
          >
            <option value="">All Media</option>
            <option value="video">Videos</option>
            <option value="audio">Audio</option>
            <option value="image">Images</option>
          </select>
          
          <select
            v-model="selectedGenre"
            @change="applyFilters"
            class="input w-auto"
          >
            <option value="">All Genres</option>
            <option v-for="genre in genres" :key="genre" :value="genre">
              {{ genre }}
            </option>
          </select>
          
          <select
            v-model="sortBy"
            @change="applyFilters"
            class="input w-auto"
          >
            <option value="created_at">Date Added</option>
            <option value="filename">Name</option>
            <option value="year">Year</option>
            <option value="duration">Duration</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="mediaStore.isLoading && mediaStore.mediaFiles.length === 0" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading media files...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="mediaStore.mediaFiles.length === 0" class="text-center py-12">
        <FilmIcon class="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No media files found
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Upload some media files to get started with your library.
        </p>
        <router-link to="/upload" class="btn-primary">
          Upload Media
        </router-link>
      </div>

      <!-- Media Grid -->
      <div v-else>
        <div class="media-grid">
          <MediaCard
            v-for="media in mediaStore.mediaFiles"
            :key="media.id"
            :media="media"
            @click="viewMedia(media)"
          />
        </div>

        <!-- Load More Button -->
        <div v-if="mediaStore.currentPage < mediaStore.totalPages" class="text-center mt-8">
          <button
            @click="loadMore"
            :disabled="mediaStore.isLoading"
            class="btn-outline"
          >
            <span v-if="mediaStore.isLoading">Loading...</span>
            <span v-else>Load More</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMediaStore } from '@/stores/media'
import MediaCard from '@/components/media/MediaCard.vue'
import { FilmIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const mediaStore = useMediaStore()

const selectedMediaType = ref('')
const selectedGenre = ref('')
const sortBy = ref('created_at')

const genres = computed(() => {
  const genreSet = new Set<string>()
  mediaStore.mediaFiles.forEach(media => {
    if (media.metadata?.genre) {
      genreSet.add(media.metadata.genre)
    }
  })
  return Array.from(genreSet).sort()
})

onMounted(async () => {
  await mediaStore.fetchMediaFiles()
})

function applyFilters() {
  const filters: any = {}
  
  if (selectedMediaType.value) {
    filters.media_type = selectedMediaType.value
  }
  
  if (selectedGenre.value) {
    filters.genre = selectedGenre.value
  }
  
  filters.sort_by = sortBy.value
  
  mediaStore.setFilters(filters)
  mediaStore.fetchMediaFiles({ page: 1 })
}

function loadMore() {
  mediaStore.loadMore()
}

function viewMedia(media: any) {
  router.push({
    name: 'MediaDetail',
    params: { id: media.id }
  })
}
</script>
