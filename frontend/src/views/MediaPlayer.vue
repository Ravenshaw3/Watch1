<template>
  <div class="media-player-page">
    <div class="player-container">
      <AdvancedVideoPlayer
        :video-src="videoSrc"
        :poster="poster"
        :subtitles="subtitles"
        @play="onPlay"
        @pause="onPause"
        @ended="onEnded"
        @timeupdate="onTimeUpdate"
        @fullscreenchange="onFullscreenChange"
      />
    </div>
    
    <!-- Media Info -->
    <div class="media-info">
      <div class="media-details">
        <h1 class="media-title">{{ media?.original_filename }}</h1>
        <div class="media-meta">
          <span class="category">{{ getCategoryDisplayName(media?.category || 'other') }}</span>
          <span class="size">{{ formatFileSize(media?.file_size || 0) }}</span>
          <span class="duration" v-if="media?.duration">{{ formatDuration(media.duration) }}</span>
        </div>
      </div>
      
      <!-- Viewing Progress -->
      <div class="viewing-progress" v-if="viewingHistory">
        <div class="progress-info">
          <span>Last watched: {{ formatDate(viewingHistory.last_watched_at) }}</span>
          <span>Progress: {{ viewingHistory.progress_percentage.toFixed(1) }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: viewingHistory.progress_percentage + '%' }"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- Related Content -->
    <div class="related-content" v-if="relatedMedia.length > 0">
      <h2>Related Content</h2>
      <div class="media-grid">
        <MediaCard
          v-for="related in relatedMedia"
          :key="related.id"
          :media="related"
          @click="playMedia(related.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { mediaApi } from '@/api/media'
import type { MediaFile, SubtitleInfo } from '@/types/media'
import AdvancedVideoPlayer from '@/components/player/AdvancedVideoPlayer.vue'
import MediaCard from '@/components/media/MediaCard.vue'

const route = useRoute()
const router = useRouter()

const media = ref<MediaFile | null>(null)
const subtitles = ref<SubtitleInfo[]>([])
const viewingHistory = ref<any>(null)
const relatedMedia = ref<MediaFile[]>([])

const videoSrc = computed(() => {
  if (!media.value) return ''
  return `http://192.168.254.14:8000/api/v1/media/${media.value.id}/stream`
})

const poster = computed(() => {
  return media.value?.artwork || ''
})

onMounted(async () => {
  const mediaId = route.params.id as string
  if (mediaId) {
    await loadMedia(mediaId)
    await loadSubtitles(mediaId)
    await loadRelatedMedia()
  }
})

async function loadMedia(mediaId: string) {
  try {
    media.value = await mediaApi.getMediaFile(mediaId)
  } catch (error) {
    console.error('Failed to load media:', error)
    router.push('/library')
  }
}

async function loadSubtitles(mediaId: string) {
  try {
    const response = await fetch(`http://192.168.254.14:8000/api/v1/media/${mediaId}/subtitles`)
    if (response.ok) {
      const subtitleData = await response.json()
      subtitles.value = subtitleData.map((sub: any) => ({
        src: sub.url,
        label: sub.language,
        language: sub.language,
        default: sub.language === 'en'
      }))
    }
  } catch (error) {
    console.error('Failed to load subtitles:', error)
  }
}

async function loadRelatedMedia() {
  if (!media.value) return
  
  try {
    const response = await mediaApi.getMediaFiles({
      category: media.value.category,
      page_size: 6
    })
    relatedMedia.value = response.media.filter(m => m.id !== media.value?.id)
  } catch (error) {
    console.error('Failed to load related media:', error)
  }
}

function playMedia(mediaId: string) {
  router.push(`/player/${mediaId}`)
}

// Event handlers
function onPlay() {
  console.log('Video started playing')
  // Track play event
}

function onPause() {
  console.log('Video paused')
  // Track pause event
}

function onEnded() {
  console.log('Video ended')
  // Track completion
}

function onTimeUpdate(currentTime: number, duration: number) {
  // Update viewing history
  updateViewingHistory(currentTime, duration)
}

function onFullscreenChange(isFullscreen: boolean) {
  console.log('Fullscreen changed:', isFullscreen)
}

async function updateViewingHistory(currentTime: number, duration: number) {
  if (!media.value) return
  
  const progressPercentage = (currentTime / duration) * 100
  const completed = progressPercentage >= 90 ? 'true' : 'partial'
  
  try {
    await fetch('http://192.168.254.14:8000/api/v1/viewing-history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        media_id: media.value.id,
        watch_duration: Math.floor(currentTime),
        current_position: Math.floor(currentTime),
        progress_percentage: progressPercentage,
        completed: completed,
        device_info: navigator.userAgent
      })
    })
  } catch (error) {
    console.error('Failed to update viewing history:', error)
  }
}

// Utility functions
function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function formatFileSize(bytes: number): string {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
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

<style scoped>
.media-player-page {
  min-height: 100vh;
  background: #000;
  color: white;
}

.player-container {
  width: 100%;
  height: 70vh;
  max-height: 800px;
}

.media-info {
  padding: 2rem;
  background: #111;
}

.media-details {
  margin-bottom: 1rem;
}

.media-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.media-meta {
  display: flex;
  gap: 1rem;
  color: #ccc;
}

.media-meta span {
  padding: 0.25rem 0.5rem;
  background: #333;
  border-radius: 4px;
  font-size: 0.875rem;
}

.viewing-progress {
  margin-top: 1rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #ccc;
}

.progress-bar {
  height: 4px;
  background: #333;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.related-content {
  padding: 2rem;
  background: #111;
}

.related-content h2 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .player-container {
    height: 50vh;
  }
  
  .media-info {
    padding: 1rem;
  }
  
  .media-title {
    font-size: 1.5rem;
  }
  
  .media-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
