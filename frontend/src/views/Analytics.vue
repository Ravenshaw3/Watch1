<template>
  <div class="analytics-page">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
        <p class="mt-2 text-gray-600">Your viewing statistics and content insights</p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading analytics...</p>
      </div>

      <!-- Analytics Content -->
      <div v-else class="space-y-8">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                    <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Total Watch Time</p>
                <p class="text-2xl font-semibold text-gray-900">{{ formatDuration(stats?.total_watch_time || 0) }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Videos Watched</p>
                <p class="text-2xl font-semibold text-gray-900">{{ stats?.total_videos || 0 }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Completed</p>
                <p class="text-2xl font-semibold text-gray-900">{{ stats?.completed_videos || 0 }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Completion Rate</p>
                <p class="text-2xl font-semibold text-gray-900">{{ formatPercentage(stats?.completion_rate) }}%</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Weekly Activity -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">This Week</h2>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Watch Time</p>
              <p class="text-2xl font-semibold text-gray-900">{{ formatDuration(stats?.weekly_watch_time || 0) }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-500">Daily Average</p>
              <p class="text-lg font-medium text-gray-900">{{ formatDuration((stats?.weekly_watch_time || 0) / 7) }}</p>
            </div>
          </div>
        </div>

        <!-- Most Watched Content -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Most Watched Content</h2>
          <div v-if="mostWatched.length === 0" class="text-center py-8">
            <p class="text-gray-500">No viewing history yet. Start watching some content!</p>
          </div>
          <div v-else class="space-y-4">
            <div 
              v-for="(item, index) in mostWatched" 
              :key="item.media_id"
              class="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
              @click="playMedia(item.media_id)"
            >
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span class="text-white font-semibold">{{ index + 1 }}</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ item.filename }}</p>
                <p class="text-xs text-gray-500">
                  {{ getCategoryDisplayName(item.category) }} • 
                  {{ formatDuration(item.total_watch_time) }} • 
                  {{ item.watch_count }} views
                </p>
              </div>
              <div class="flex-shrink-0 text-right">
                <p class="text-sm font-medium text-gray-900">{{ formatPercentage(item.max_progress) }}%</p>
                <p class="text-xs text-gray-500">max progress</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div v-if="recentHistory.length === 0" class="text-center py-8">
            <p class="text-gray-500">No recent activity. Start watching some content!</p>
          </div>
          <div v-else class="space-y-3">
            <div 
              v-for="item in recentHistory" 
              :key="item.id"
              class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-gray-300 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 5v10l8-5-8-5z"/>
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ item.filename }}</p>
                <p class="text-xs text-gray-500">
                  {{ formatDate(item.last_watched_at) }} • 
                  {{ formatPercentage(item.progress_percentage) }}% complete
                </p>
              </div>
              <div class="flex-shrink-0">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': item.completed === 'true',
                    'bg-yellow-100 text-yellow-800': item.completed === 'partial',
                    'bg-gray-100 text-gray-800': item.completed === 'false'
                  }"
                >
                  {{ item.completed === 'true' ? 'Completed' : item.completed === 'partial' ? 'In Progress' : 'Started' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'

const router = useRouter()

const isLoading = ref(true)
const stats = ref<any>(null)
const mostWatched = ref<any[]>([])
const recentHistory = ref<any[]>([])

onMounted(async () => {
  await loadAnalytics()
})

async function loadAnalytics() {
  isLoading.value = true
  
  // Add timeout protection
  const timeoutId = setTimeout(() => {
    console.warn('Analytics loading timeout - forcing completion')
    isLoading.value = false
  }, 10000) // 10 second timeout
  
  try {
    console.log('Loading analytics data...')
    // Use the proper API client instead of hardcoded fetch
    const response = await apiClient.get('/analytics/dashboard')
    console.log('Analytics response received:', response.data)
    
    if (response.data) {
      // Map the backend response to frontend expectations
      stats.value = {
        total_watch_time: response.data.total_media_files * 3600, // Mock data
        total_videos: response.data.total_media_files,
        completed_videos: Math.floor(response.data.total_media_files * 0.7), // Mock 70% completion
        completion_rate: 70.5, // Mock completion rate
        weekly_watch_time: 25200 // Mock 7 hours this week
      }
      
      // Mock most watched data based on categories
      mostWatched.value = Object.entries(response.data.media_by_category || {}).map(([category, count], index) => ({
        media_id: `mock-${index}`,
        title: `Top ${category} Content`,
        category: category,
        total_watch_time: (count as number) * 1800, // Mock watch time
        watch_count: count,
        max_progress: 85.5 + (index * 2) // Mock progress
      })).slice(0, 5)
      
      // Mock recent history
      recentHistory.value = [
        {
          id: 'recent-1',
          filename: 'Recent Movie.mkv',
          last_watched_at: new Date().toISOString(),
          completed: 'partial',
          progress_percentage: 67.5
        },
        {
          id: 'recent-2', 
          filename: 'Another Video.mp4',
          last_watched_at: new Date(Date.now() - 86400000).toISOString(),
          completed: 'true',
          progress_percentage: 100.0
        }
      ]
    }

  } catch (error) {
    console.error('Failed to load analytics:', error)
    // Set default empty state
    stats.value = {
      total_watch_time: 0,
      total_videos: 0,
      completed_videos: 0,
      completion_rate: 0,
      weekly_watch_time: 0
    }
    mostWatched.value = []
    recentHistory.value = []
  } finally {
    clearTimeout(timeoutId)
    isLoading.value = false
    console.log('Analytics loading completed')
  }
}

function playMedia(mediaId: string) {
  router.push(`/player/${mediaId}`)
}

function formatDuration(seconds: number): string {
  const safeSeconds = Number(seconds) || 0
  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

function formatPercentage(value: any): string {
  const numValue = Number(value)
  if (isNaN(numValue)) {
    return '0.0'
  }
  return numValue.toFixed(1)
}

function getCategoryDisplayName(category: string): string {
  const categoryMap: Record<string, string> = {
    'movies': 'Movie',
    'tv-shows': 'TV Show',
    'kids': 'Kids',
    'music-videos': 'Music Video',
    'documentaries': 'Documentary',
    'sports': 'Sports',
    'anime': 'Anime',
    'other': 'Other'
  }
  return categoryMap[category] || category
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}
</script>
