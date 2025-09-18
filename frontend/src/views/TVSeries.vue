<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          TV Series
        </h1>
        <p class="mt-2 text-gray-600">
          Browse and watch your TV show collection
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading TV series...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="tvSeries.length === 0" class="text-center py-12">
        <FilmIcon class="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          No TV series found
        </h3>
        <p class="text-gray-600 mb-6">
          Scan your media directory to discover TV shows.
        </p>
        <button @click="scanMedia" class="btn-primary">
          Scan Media Directory
        </button>
      </div>

      <!-- TV Series Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="series in tvSeries"
          :key="series.series_name"
          class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
          @click="selectSeries(series)"
        >
          <!-- Series Artwork -->
          <div class="aspect-[3/4] bg-gray-200 flex items-center justify-center">
            <FilmIcon class="h-16 w-16 text-gray-400" />
          </div>

          <!-- Series Info -->
          <div class="p-4">
            <h3 class="font-semibold text-lg text-gray-900 mb-2">
              {{ series.series_name }}
            </h3>
            <div class="text-sm text-gray-600">
              <p>{{ Object.keys(series.seasons).length }} Season{{ Object.keys(series.seasons).length !== 1 ? 's' : '' }}</p>
              <p>{{ getTotalEpisodes(series) }} Episode{{ getTotalEpisodes(series) !== 1 ? 's' : '' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Series Detail Modal -->
      <div v-if="selectedSeries" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ selectedSeries.series_name }}
            </h2>
            <button @click="selectedSeries = null" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>

          <!-- Seasons -->
          <div v-for="(episodes, seasonNum) in selectedSeries.seasons" :key="seasonNum" class="mb-8">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">
              Season {{ seasonNum }}
            </h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="episode in episodes"
                :key="episode.id"
                class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
                @click="playEpisode(episode)"
              >
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <div class="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                      <span class="text-white font-semibold text-sm">
                        E{{ episode.episode.toString().padStart(2, '0') }}
                      </span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ episode.filename }}
                    </p>
                    <p v-if="episode.duration" class="text-xs text-gray-500">
                      {{ formatDuration(episode.duration) }}
                    </p>
                  </div>
                  <div class="flex-shrink-0">
                    <PlayIcon class="h-5 w-5 text-gray-400 hover:text-primary-600" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Play All Button -->
          <div class="mt-6 pt-6 border-t border-gray-200">
            <button
              @click="playAllEpisodes"
              class="btn-primary w-full"
            >
              <PlayIcon class="h-5 w-5 mr-2" />
              Play All Episodes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mediaApi } from '@/api/media'
import type { TVSeries } from '@/types/media'
import { FilmIcon, PlayIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const tvSeries = ref<TVSeries[]>([])
const selectedSeries = ref<TVSeries | null>(null)
const isLoading = ref(false)

async function loadTVSeries() {
  isLoading.value = true
  try {
    const response = await mediaApi.getTVSeries()
    tvSeries.value = response.series
  } catch (error) {
    console.error('Failed to load TV series:', error)
  } finally {
    isLoading.value = false
  }
}

function selectSeries(series: TVSeries) {
  selectedSeries.value = series
}

function getTotalEpisodes(series: TVSeries): number {
  return Object.values(series.seasons).reduce((total, episodes) => total + episodes.length, 0)
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

async function playEpisode(episode: any) {
  try {
    const streamUrl = await mediaApi.streamMediaFile(episode.id)
        const fullUrl = `http://localhost:8000${streamUrl}`
    window.open(fullUrl, '_blank')
  } catch (error) {
    console.error('Failed to play episode:', error)
  }
}

async function playAllEpisodes() {
  if (!selectedSeries.value) return
  
  // Get all episodes in order
  const allEpisodes = []
  for (const seasonNum of Object.keys(selectedSeries.value.seasons).sort((a, b) => parseInt(a) - parseInt(b))) {
    const episodes = selectedSeries.value.seasons[parseInt(seasonNum)]
    allEpisodes.push(...episodes.sort((a, b) => a.episode - b.episode))
  }
  
  // Play first episode
  if (allEpisodes.length > 0) {
    await playEpisode(allEpisodes[0])
  }
}

async function scanMedia() {
  try {
    await mediaApi.scanMediaDirectory()
    await loadTVSeries()
  } catch (error) {
    console.error('Failed to scan media:', error)
  }
}

onMounted(() => {
  loadTVSeries()
})
</script>
