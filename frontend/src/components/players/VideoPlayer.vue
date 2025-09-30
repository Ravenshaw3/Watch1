<template>
  <div class="video-player-container">
    <div class="video-wrapper" ref="videoWrapper">
      <video
        ref="videoElement"
        class="video-player"
        :poster="posterUrl"
        controls
        preload="metadata"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
        @error="onError"
        @play="onPlay"
        @pause="onPause"
      >
        <source :src="videoUrl" type="video/mp4" />
        <source :src="videoUrl" type="video/webm" />
        <source :src="videoUrl" type="video/ogg" />
        Your browser does not support the video tag.
      </video>

      <!-- Custom Controls Overlay -->
      <div v-if="showCustomControls" class="custom-controls">
        <div class="controls-background"></div>
        
        <!-- Play/Pause Button -->
        <button
          @click="togglePlayPause"
          class="play-pause-btn"
        >
          <PlayIcon v-if="!isPlaying" class="h-12 w-12" />
          <PauseIcon v-else class="h-12 w-12" />
        </button>

        <!-- Progress Bar -->
        <div class="progress-container">
          <div class="progress-bar" @click="seekToPosition">
            <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
            <div class="progress-handle" :style="{ left: progressPercent + '%' }"></div>
          </div>
          <div class="time-display">
            <span>{{ formatTime(currentTime) }}</span>
            <span>/</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>

        <!-- Volume Control -->
        <div class="volume-control">
          <button @click="toggleMute" class="volume-btn">
            <SpeakerWaveIcon v-if="!isMuted && volume > 0.5" class="h-5 w-5" />
            <SpeakerXMarkIcon v-else-if="isMuted || volume === 0" class="h-5 w-5" />
            <SpeakerWaveIcon v-else class="h-5 w-5" />
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            v-model="volume"
            @input="updateVolume"
            class="volume-slider"
          />
        </div>

        <!-- Fullscreen Button -->
        <button @click="toggleFullscreen" class="fullscreen-btn">
          <ArrowsPointingOutIcon v-if="!isFullscreen" class="h-5 w-5" />
          <ArrowsPointingInIcon v-else class="h-5 w-5" />
        </button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>

      <!-- Error Message -->
      <div v-if="hasError" class="error-overlay">
        <ExclamationTriangleIcon class="h-12 w-12 text-red-500 mb-4" />
        <p class="text-white text-lg">Failed to load video</p>
        <p class="text-gray-300 text-sm">{{ errorMessage }}</p>
      </div>
    </div>

    <!-- Video Information -->
    <div v-if="showInfo" class="video-info">
      <h3 class="video-title">{{ media?.title || media?.filename || 'Unknown Video' }}</h3>
      <div class="video-meta">
        <span v-if="media?.duration" class="meta-item">
          Duration: {{ formatTime(media.duration) }}
        </span>
        <span v-if="media?.file_size" class="meta-item">
          Size: {{ formatFileSize(media.file_size) }}
        </span>
        <span v-if="videoResolution" class="meta-item">
          Resolution: {{ videoResolution }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  PlayIcon,
  PauseIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import type { MediaFile } from '@/types/media'

interface Props {
  media: MediaFile
  autoplay?: boolean
  showCustomControls?: boolean
  showInfo?: boolean
}

interface Emits {
  (e: 'play'): void
  (e: 'pause'): void
  (e: 'ended'): void
  (e: 'error', error: string): void
  (e: 'timeupdate', time: number): void
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: false,
  showCustomControls: false,
  showInfo: true
})

const emit = defineEmits<Emits>()

// Refs
const videoElement = ref<HTMLVideoElement | null>(null)
const videoWrapper = ref<HTMLDivElement | null>(null)

// State
const isPlaying = ref(false)
const isLoading = ref(true)
const hasError = ref(false)
const errorMessage = ref('')
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const isMuted = ref(false)
const isFullscreen = ref(false)
const videoResolution = ref('')

// Computed
const videoUrl = computed(() => {
  if (!props.media?.id) return ''
  
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${props.media.id}/stream?token=${token}`
})

const posterUrl = computed(() => {
  if (!props.media?.id) return ''
  
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${props.media.id}/poster?token=${token}`
})

const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

// Methods
function togglePlayPause() {
  if (!videoElement.value) return
  
  if (isPlaying.value) {
    videoElement.value.pause()
  } else {
    videoElement.value.play()
  }
}

function toggleMute() {
  if (!videoElement.value) return
  
  isMuted.value = !isMuted.value
  videoElement.value.muted = isMuted.value
}

function updateVolume() {
  if (!videoElement.value) return
  
  videoElement.value.volume = volume.value
  isMuted.value = volume.value === 0
}

function seekToPosition(event: MouseEvent) {
  if (!videoElement.value || !duration.value) return
  
  const progressBar = event.currentTarget as HTMLElement
  const rect = progressBar.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percent = clickX / rect.width
  const newTime = percent * duration.value
  
  videoElement.value.currentTime = newTime
}

function toggleFullscreen() {
  if (!videoWrapper.value) return
  
  if (!isFullscreen.value) {
    if (videoWrapper.value.requestFullscreen) {
      videoWrapper.value.requestFullscreen()
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

// Event Handlers
function onLoadedMetadata() {
  if (!videoElement.value) return
  
  isLoading.value = false
  duration.value = videoElement.value.duration
  
  // Get video resolution
  videoResolution.value = `${videoElement.value.videoWidth}x${videoElement.value.videoHeight}`
  
  if (props.autoplay) {
    videoElement.value.play()
  }
}

function onTimeUpdate() {
  if (!videoElement.value) return
  
  currentTime.value = videoElement.value.currentTime
  emit('timeupdate', currentTime.value)
}

function onPlay() {
  isPlaying.value = true
  emit('play')
}

function onPause() {
  isPlaying.value = false
  emit('pause')
}

function onEnded() {
  isPlaying.value = false
  emit('ended')
}

function onError(event: Event) {
  hasError.value = true
  isLoading.value = false
  
  const video = event.target as HTMLVideoElement
  const error = video.error
  
  if (error) {
    switch (error.code) {
      case error.MEDIA_ERR_ABORTED:
        errorMessage.value = 'Video playback was aborted'
        break
      case error.MEDIA_ERR_NETWORK:
        errorMessage.value = 'Network error occurred'
        break
      case error.MEDIA_ERR_DECODE:
        errorMessage.value = 'Video format not supported'
        break
      case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
        errorMessage.value = 'Video source not supported'
        break
      default:
        errorMessage.value = 'Unknown error occurred'
    }
  } else {
    errorMessage.value = 'Failed to load video'
  }
  
  emit('error', errorMessage.value)
}

// Utility Functions
function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Fullscreen event listeners
function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

// Lifecycle
onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  
  if (videoElement.value) {
    videoElement.value.volume = volume.value
  }
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})

// Media changes handled in onMounted and event handlers
</script>

<style scoped>
.video-player-container {
  @apply w-full bg-black rounded-lg overflow-hidden;
}

.video-wrapper {
  @apply relative w-full;
  aspect-ratio: 16/9;
}

.video-player {
  @apply w-full h-full object-contain;
}

.custom-controls {
  @apply absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300;
}

.controls-background {
  @apply absolute inset-0 bg-black bg-opacity-50;
}

.play-pause-btn {
  @apply relative z-10 text-white hover:text-primary-400 transition-colors;
}

.progress-container {
  @apply absolute bottom-4 left-4 right-4 z-10;
}

.progress-bar {
  @apply relative w-full h-2 bg-gray-600 rounded-full cursor-pointer mb-2;
}

.progress-filled {
  @apply h-full bg-primary-500 rounded-full transition-all duration-150;
}

.progress-handle {
  @apply absolute top-1/2 w-4 h-4 bg-primary-500 rounded-full transform -translate-y-1/2 -translate-x-1/2;
}

.time-display {
  @apply flex justify-between text-white text-sm;
}

.volume-control {
  @apply absolute bottom-4 right-20 z-10 flex items-center space-x-2;
}

.volume-btn {
  @apply text-white hover:text-primary-400 transition-colors;
}

.volume-slider {
  @apply w-20;
}

.fullscreen-btn {
  @apply absolute bottom-4 right-4 z-10 text-white hover:text-primary-400 transition-colors;
}

.loading-overlay {
  @apply absolute inset-0 flex items-center justify-center bg-black bg-opacity-75;
}

.error-overlay {
  @apply absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-75 text-center p-4;
}

.video-info {
  @apply p-4 bg-gray-900 text-white;
}

.video-title {
  @apply text-lg font-semibold mb-2;
}

.video-meta {
  @apply flex flex-wrap gap-4 text-sm text-gray-300;
}

.meta-item {
  @apply flex items-center;
}
</style>
