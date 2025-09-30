<template>
  <div class="media-player-page">
    <div class="player-container">
      <div v-if="!media" class="error-message">
        <h2>Media Not Found</h2>
        <p>The requested media file could not be loaded.</p>
        <button @click="router.push('/library')" class="btn-primary">Back to Library</button>
      </div>
      <EnhancedVideoPlayer
        v-else
        ref="videoPlayerRef"
        :video-src="videoSrc"
        :poster="poster"
        :subtitles="subtitles"
        :video-title="media?.original_filename"
        :autoplay="false"
        @play="onPlay"
        @pause="onPause"
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
        @fullscreenchange="onFullscreenChange"
      />
      
      <!-- Resume Dialog -->
      <div v-if="showResumeDialog" class="resume-dialog-overlay">
        <div class="resume-dialog">
          <div class="resume-header">
            <h3>Resume Playback</h3>
          </div>
          <div class="resume-content">
            <p>You were watching this video. Would you like to resume where you left off?</p>
            <div class="resume-info">
              <span class="resume-time">{{ formatTime(viewingHistory?.current_position || 0) }}</span>
              <span class="resume-progress">{{ viewingHistory?.progress_percentage?.toFixed(1) }}% complete</span>
            </div>
          </div>
          <div class="resume-actions">
            <button @click="startFromBeginning" class="resume-btn secondary">Start Over</button>
            <button @click="resumePlayback" class="resume-btn primary">Resume</button>
          </div>
        </div>
      </div>
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
import { getMediaSubtitles, convertToSubtitleTracks } from '@/api/subtitles'
import type { MediaFile, SubtitleInfo, MediaCategory } from '@/types/media'
import EnhancedVideoPlayer from '@/components/player/EnhancedVideoPlayer.vue'
import MediaCard from '@/components/MediaCardNew.vue'

const route = useRoute()
const router = useRouter()

const media = ref<MediaFile | null>(null)
const subtitles = ref<SubtitleInfo[]>([])
const viewingHistory = ref<any>(null)
const relatedMedia = ref<MediaFile[]>([])
const videoPlayerRef = ref<any>(null)
const showResumeDialog = ref(false)

const videoSrc = computed(() => {
  if (!media.value) return ''
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'
  const token = localStorage.getItem('access_token')
  return `${baseUrl}/api/v1/media/${media.value.id}/stream?token=${token}`
})

const poster = computed(() => {
  return media.value?.artwork || ''
})

onMounted(async () => {
  const mediaId = route.params.id as string
  if (mediaId) {
    await loadMedia(mediaId)
    await loadSubtitles(mediaId)
    await loadViewingHistory()
    await loadRelatedMedia()
  }
})

async function loadMedia(mediaId: string) {
  try {
    console.log('Loading media with ID:', mediaId)
    media.value = await mediaApi.getMediaFile(mediaId)
    console.log('Media loaded successfully:', media.value)
  } catch (error) {
    console.error('Failed to load media:', error)
    console.error('Media ID that failed:', mediaId)
    // Don't redirect immediately, show error message instead
    // router.push('/library')
  }
}

async function loadSubtitles(mediaId: string) {
  try {
    const subtitleData = await getMediaSubtitles(mediaId)
    subtitles.value = convertToSubtitleTracks(subtitleData, mediaId)
    console.log(`Loaded ${subtitles.value.length} subtitle tracks for media ${mediaId}`)
  } catch (error) {
    console.error('Failed to load subtitles:', error)
    subtitles.value = []
  }
}

async function loadRelatedMedia() {
  if (!media.value) return
  
  try {
    const response = await mediaApi.getMediaFiles({
      category: media.value.category as MediaCategory,
      page_size: 6
    })
    const mediaList = response.media ?? response.items ?? []
    relatedMedia.value = mediaList.filter(m => m.id !== media.value?.id)
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
    const response = await fetch('http://localhost:8000/api/v1/viewing-history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
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
    
    if (response.ok) {
      const historyData = await response.json()
      viewingHistory.value = historyData
    }
  } catch (error) {
    console.error('Failed to update viewing history:', error)
  }
}

async function loadViewingHistory() {
  if (!media.value) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/v1/viewing-history/${media.value.id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.ok) {
      const historyData = await response.json()
      viewingHistory.value = historyData
      
      // Auto-resume if there's significant progress (more than 5% but less than 90%)
      if (historyData.progress_percentage > 5 && historyData.progress_percentage < 90) {
        showResumeDialog.value = true
      }
    }
  } catch (error) {
    console.error('Failed to load viewing history:', error)
  }
}

function resumePlayback() {
  if (viewingHistory.value && videoPlayerRef.value) {
    const resumeTime = viewingHistory.value.current_position
    // Use the video element directly to seek
    const videoElement = videoPlayerRef.value.$refs?.videoElement
    if (videoElement) {
      videoElement.currentTime = resumeTime
    }
    showResumeDialog.value = false
  }
}

function startFromBeginning() {
  showResumeDialog.value = false
}

function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
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

.resume-dialog-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.resume-dialog {
  background: #1f2937;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  color: white;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.resume-header h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.resume-content p {
  margin: 0 0 1rem 0;
  color: #d1d5db;
  line-height: 1.5;
}

.resume-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.resume-time {
  font-weight: 600;
  color: #3b82f6;
  font-size: 1.1rem;
}

.resume-progress {
  font-size: 0.875rem;
  color: #9ca3af;
}

.resume-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.resume-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.resume-btn.secondary {
  background: #374151;
  color: white;
}

.resume-btn.secondary:hover {
  background: #4b5563;
}

.resume-btn.primary {
  background: #3b82f6;
  color: white;
}

.resume-btn.primary:hover {
  background: #2563eb;
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
  
  .resume-dialog {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .resume-actions {
    flex-direction: column;
  }
  
  .resume-btn {
    width: 100%;
  }
}
</style>
