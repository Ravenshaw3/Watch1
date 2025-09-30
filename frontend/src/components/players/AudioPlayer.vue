<template>
  <div class="audio-player-container">
    <!-- Audio Element -->
    <audio
      ref="audioElement"
      :src="audioUrl"
      preload="metadata"
      @loadedmetadata="onLoadedMetadata"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @error="onError"
      @play="onPlay"
      @pause="onPause"
    ></audio>

    <!-- Player Interface -->
    <div class="audio-player">
      <!-- Album Art / Visualization -->
      <div class="album-art-container">
        <div class="album-art">
          <img
            v-if="albumArtUrl && !imageError"
            :src="albumArtUrl"
            :alt="displayTitle"
            class="album-image"
            @error="onImageError"
          />
          <div v-else class="album-placeholder">
            <MusicalNoteIcon class="h-16 w-16 text-gray-400" />
          </div>
          
          <!-- Vinyl Record Effect -->
          <div v-if="isPlaying" class="vinyl-record">
            <div class="vinyl-center"></div>
          </div>
        </div>
        
        <!-- Waveform Visualization -->
        <div v-if="showWaveform" class="waveform-container">
          <canvas ref="waveformCanvas" class="waveform-canvas"></canvas>
        </div>
      </div>

      <!-- Track Information -->
      <div class="track-info">
        <h3 class="track-title">{{ displayTitle }}</h3>
        <p class="track-artist">{{ displayArtist }}</p>
        <p class="track-album">{{ displayAlbum }}</p>
      </div>

      <!-- Controls -->
      <div class="audio-controls">
        <!-- Previous Track -->
        <button
          @click="previousTrack"
          :disabled="!hasPrevious"
          class="control-btn"
          :class="{ 'opacity-50': !hasPrevious }"
        >
          <BackwardIcon class="h-6 w-6" />
        </button>

        <!-- Play/Pause -->
        <button
          @click="togglePlayPause"
          class="play-pause-btn"
        >
          <PlayIcon v-if="!isPlaying" class="h-8 w-8" />
          <PauseIcon v-else class="h-8 w-8" />
        </button>

        <!-- Next Track -->
        <button
          @click="nextTrack"
          :disabled="!hasNext"
          class="control-btn"
          :class="{ 'opacity-50': !hasNext }"
        >
          <ForwardIcon class="h-6 w-6" />
        </button>

        <!-- Shuffle -->
        <button
          @click="toggleShuffle"
          class="control-btn"
          :class="{ 'text-primary-500': isShuffled }"
        >
          <ArrowPathRoundedSquareIcon class="h-5 w-5" />
        </button>

        <!-- Repeat -->
        <button
          @click="toggleRepeat"
          class="control-btn"
          :class="{ 'text-primary-500': repeatMode !== 'none' }"
        >
          <ArrowPathIcon class="h-5 w-5" />
          <span v-if="repeatMode === 'one'" class="repeat-indicator">1</span>
        </button>
      </div>

      <!-- Progress Bar -->
      <div class="progress-section">
        <div class="time-display">
          <span class="current-time">{{ formatTime(currentTime) }}</span>
          <span class="total-time">{{ formatTime(duration) }}</span>
        </div>
        <div class="progress-bar" @click="seekToPosition">
          <div class="progress-track"></div>
          <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
          <div class="progress-handle" :style="{ left: progressPercent + '%' }"></div>
        </div>
      </div>

      <!-- Volume and Additional Controls -->
      <div class="secondary-controls">
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
            step="0.05"
            v-model="volume"
            @input="updateVolume"
            class="volume-slider"
          />
          <span class="volume-percent">{{ Math.round(volume * 100) }}%</span>
        </div>

        <!-- Playback Speed -->
        <div class="speed-control">
          <select v-model="playbackSpeed" @change="updatePlaybackSpeed" class="speed-select">
            <option value="0.5">0.5x</option>
            <option value="0.75">0.75x</option>
            <option value="1">1x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
          </select>
        </div>

        <!-- Equalizer Toggle -->
        <button
          @click="toggleEqualizer"
          class="control-btn"
          :class="{ 'text-primary-500': showEqualizer }"
        >
          <Bars3Icon class="h-5 w-5" />
        </button>
      </div>

      <!-- Equalizer -->
      <div v-if="showEqualizer" class="equalizer-section">
        <div class="equalizer-controls">
          <div
            v-for="(band, index) in equalizerBands"
            :key="index"
            class="eq-band"
          >
            <input
              type="range"
              min="-12"
              max="12"
              step="0.5"
              v-model="band.gain"
              @input="updateEqualizer"
              class="eq-slider"
              orient="vertical"
            />
            <label class="eq-label">{{ band.frequency }}</label>
          </div>
        </div>
        <button @click="resetEqualizer" class="eq-reset-btn">
          Reset EQ
        </button>
      </div>

      <!-- Loading/Error States -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-600">Loading audio...</p>
      </div>

      <div v-if="hasError" class="error-overlay">
        <ExclamationTriangleIcon class="h-8 w-8 text-red-500 mb-2" />
        <p class="text-red-600 text-sm">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  PlayIcon,
  PauseIcon,
  BackwardIcon,
  ForwardIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  ArrowPathIcon,
  ArrowPathRoundedSquareIcon,
  MusicalNoteIcon,
  Bars3Icon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import type { MediaFile } from '@/types/media'

interface Props {
  media: MediaFile
  playlist?: MediaFile[]
  autoplay?: boolean
  showWaveform?: boolean
}

interface Emits {
  (e: 'play'): void
  (e: 'pause'): void
  (e: 'ended'): void
  (e: 'error', error: string): void
  (e: 'track-changed', media: MediaFile): void
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: false,
  showWaveform: false
})

const emit = defineEmits<Emits>()

// Refs
const audioElement = ref<HTMLAudioElement | null>(null)
const waveformCanvas = ref<HTMLCanvasElement | null>(null)

// State
const isPlaying = ref(false)
const isLoading = ref(true)
const hasError = ref(false)
const errorMessage = ref('')
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(0.8)
const isMuted = ref(false)
const playbackSpeed = ref(1)
const imageError = ref(false)

// Playback modes
const isShuffled = ref(false)
const repeatMode = ref<'none' | 'all' | 'one'>('none')

// Equalizer
const showEqualizer = ref(false)
const equalizerBands = ref([
  { frequency: '60Hz', gain: 0 },
  { frequency: '170Hz', gain: 0 },
  { frequency: '310Hz', gain: 0 },
  { frequency: '600Hz', gain: 0 },
  { frequency: '1kHz', gain: 0 },
  { frequency: '3kHz', gain: 0 },
  { frequency: '6kHz', gain: 0 },
  { frequency: '12kHz', gain: 0 },
  { frequency: '14kHz', gain: 0 },
  { frequency: '16kHz', gain: 0 }
])

// Computed
const audioUrl = computed(() => {
  if (!props.media?.id) return ''
  
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${props.media.id}/stream?token=${token}`
})

const albumArtUrl = computed(() => {
  if (!props.media?.id) return ''
  
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${props.media.id}/poster?token=${token}`
})

const displayTitle = computed(() => {
  return props.media?.title || props.media?.filename || 'Unknown Track'
})

const displayArtist = computed(() => {
  // Extract artist from metadata or filename
  return props.media?.metadata?.artist || 'Unknown Artist'
})

const displayAlbum = computed(() => {
  // Extract album from metadata
  return props.media?.metadata?.album || 'Unknown Album'
})

const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

const currentTrackIndex = computed(() => {
  if (!props.playlist) return -1
  return props.playlist.findIndex(track => track.id === props.media.id)
})

const hasPrevious = computed(() => {
  return props.playlist && currentTrackIndex.value > 0
})

const hasNext = computed(() => {
  return props.playlist && currentTrackIndex.value < props.playlist.length - 1
})

// Methods
function togglePlayPause() {
  if (!audioElement.value) return
  
  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    audioElement.value.play()
  }
}

function previousTrack() {
  if (!props.playlist || !hasPrevious.value) return
  
  const prevTrack = props.playlist[currentTrackIndex.value - 1]
  emit('track-changed', prevTrack)
}

function nextTrack() {
  if (!props.playlist || !hasNext.value) return
  
  const nextTrack = props.playlist[currentTrackIndex.value + 1]
  emit('track-changed', nextTrack)
}

function toggleShuffle() {
  isShuffled.value = !isShuffled.value
}

function toggleRepeat() {
  switch (repeatMode.value) {
    case 'none':
      repeatMode.value = 'all'
      break
    case 'all':
      repeatMode.value = 'one'
      break
    case 'one':
      repeatMode.value = 'none'
      break
  }
}

function toggleMute() {
  if (!audioElement.value) return
  
  isMuted.value = !isMuted.value
  audioElement.value.muted = isMuted.value
}

function updateVolume() {
  if (!audioElement.value) return
  
  audioElement.value.volume = volume.value
  isMuted.value = volume.value === 0
}

function updatePlaybackSpeed() {
  if (!audioElement.value) return
  
  audioElement.value.playbackRate = playbackSpeed.value
}

function seekToPosition(event: MouseEvent) {
  if (!audioElement.value || !duration.value) return
  
  const progressBar = event.currentTarget as HTMLElement
  const rect = progressBar.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percent = clickX / rect.width
  const newTime = percent * duration.value
  
  audioElement.value.currentTime = newTime
}

function toggleEqualizer() {
  showEqualizer.value = !showEqualizer.value
}

function updateEqualizer() {
  // Placeholder for equalizer implementation
  console.log('Equalizer updated:', equalizerBands.value)
}

function resetEqualizer() {
  equalizerBands.value.forEach(band => {
    band.gain = 0
  })
  updateEqualizer()
}

// Event Handlers
function onLoadedMetadata() {
  if (!audioElement.value) return
  
  isLoading.value = false
  duration.value = audioElement.value.duration
  
  if (props.autoplay) {
    audioElement.value.play()
  }
}

function onTimeUpdate() {
  if (!audioElement.value) return
  
  currentTime.value = audioElement.value.currentTime
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
  
  // Handle repeat modes
  if (repeatMode.value === 'one') {
    if (audioElement.value) {
      audioElement.value.currentTime = 0
      audioElement.value.play()
    }
  } else if (repeatMode.value === 'all' && hasNext.value) {
    nextTrack()
  }
}

function onError(event: Event) {
  hasError.value = true
  isLoading.value = false
  
  const audio = event.target as HTMLAudioElement
  const error = audio.error
  
  if (error) {
    switch (error.code) {
      case error.MEDIA_ERR_ABORTED:
        errorMessage.value = 'Audio playback was aborted'
        break
      case error.MEDIA_ERR_NETWORK:
        errorMessage.value = 'Network error occurred'
        break
      case error.MEDIA_ERR_DECODE:
        errorMessage.value = 'Audio format not supported'
        break
      case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
        errorMessage.value = 'Audio source not supported'
        break
      default:
        errorMessage.value = 'Unknown error occurred'
    }
  } else {
    errorMessage.value = 'Failed to load audio'
  }
  
  emit('error', errorMessage.value)
}

function onImageError() {
  imageError.value = true
}

// Utility Functions
function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00'
  
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// Lifecycle
onMounted(() => {
  if (audioElement.value) {
    audioElement.value.volume = volume.value
    audioElement.value.playbackRate = playbackSpeed.value
  }
})

// Media changes handled in onMounted
</script>

<style scoped>
.audio-player-container {
  @apply w-full max-w-2xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden;
}

.audio-player {
  @apply p-6;
}

.album-art-container {
  @apply relative mb-6;
}

.album-art {
  @apply relative w-48 h-48 mx-auto mb-4 rounded-lg overflow-hidden shadow-lg;
}

.album-image {
  @apply w-full h-full object-cover;
}

.album-placeholder {
  @apply w-full h-full flex items-center justify-center bg-gray-200;
}

.vinyl-record {
  @apply absolute inset-0 border-4 border-gray-800 rounded-full animate-spin;
  animation-duration: 2s;
}

.vinyl-center {
  @apply absolute top-1/2 left-1/2 w-8 h-8 bg-gray-800 rounded-full transform -translate-x-1/2 -translate-y-1/2;
}

.waveform-container {
  @apply mt-4;
}

.waveform-canvas {
  @apply w-full h-16 bg-gray-100 rounded;
}

.track-info {
  @apply text-center mb-6;
}

.track-title {
  @apply text-xl font-bold text-gray-900 mb-1;
}

.track-artist {
  @apply text-lg text-gray-700 mb-1;
}

.track-album {
  @apply text-sm text-gray-500;
}

.audio-controls {
  @apply flex items-center justify-center space-x-4 mb-6;
}

.control-btn {
  @apply text-gray-600 hover:text-primary-600 transition-colors;
}

.play-pause-btn {
  @apply bg-primary-600 text-white p-3 rounded-full hover:bg-primary-700 transition-colors;
}

.repeat-indicator {
  @apply absolute -top-1 -right-1 text-xs bg-primary-600 text-white rounded-full w-4 h-4 flex items-center justify-center;
}

.progress-section {
  @apply mb-4;
}

.time-display {
  @apply flex justify-between text-sm text-gray-600 mb-2;
}

.progress-bar {
  @apply relative w-full h-2 cursor-pointer;
}

.progress-track {
  @apply absolute inset-0 bg-gray-300 rounded-full;
}

.progress-filled {
  @apply absolute left-0 top-0 h-full bg-primary-500 rounded-full transition-all duration-150;
}

.progress-handle {
  @apply absolute top-1/2 w-4 h-4 bg-primary-600 rounded-full transform -translate-y-1/2 -translate-x-1/2 shadow-lg;
}

.secondary-controls {
  @apply flex items-center justify-between;
}

.volume-control {
  @apply flex items-center space-x-2;
}

.volume-btn {
  @apply text-gray-600 hover:text-primary-600 transition-colors;
}

.volume-slider {
  @apply w-20;
}

.volume-percent {
  @apply text-xs text-gray-500 w-8;
}

.speed-control {
  @apply flex items-center space-x-2;
}

.speed-select {
  @apply text-sm border border-gray-300 rounded px-2 py-1;
}

.equalizer-section {
  @apply mt-6 p-4 bg-gray-50 rounded-lg;
}

.equalizer-controls {
  @apply flex justify-center space-x-2 mb-4;
}

.eq-band {
  @apply flex flex-col items-center;
}

.eq-slider {
  @apply h-20 w-4;
  writing-mode: bt-lr; /* IE */
  -webkit-appearance: slider-vertical; /* WebKit */
}

.eq-label {
  @apply text-xs text-gray-600 mt-2;
}

.eq-reset-btn {
  @apply btn-outline text-sm mx-auto block;
}

.loading-overlay,
.error-overlay {
  @apply flex flex-col items-center justify-center py-8;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 px-3 py-1 rounded hover:bg-gray-50 transition-colors;
}
</style>
