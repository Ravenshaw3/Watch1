<template>
  <div class="enhanced-video-player" ref="playerContainer">
    <div class="video-wrapper">
      <video
        ref="videoElement"
        :src="videoSrc"
        :poster="poster"
        class="video-element"
        preload="metadata"
        crossorigin="anonymous"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
        @play="onPlay"
        @pause="onPause"
        @click="togglePlayPause"
        @dblclick="toggleFullscreen"
        @waiting="onWaiting"
        @playing="onPlaying"
        @progress="onProgress"
        @error="onError"
      >
        <track
          v-for="(subtitle, index) in subtitles"
          :key="index"
          :src="subtitle.src"
          :label="subtitle.label"
          :srclang="subtitle.language"
          :default="subtitle.default"
          kind="subtitles"
        />
      </video>

      <!-- Loading Overlay -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Loading video...</div>
      </div>

      <!-- Controls Overlay -->
      <div class="controls-overlay" :class="{ 'visible': showControls }">
        <!-- Top Controls -->
        <div class="top-controls">
          <div class="video-title">{{ videoTitle || 'Video Player' }}</div>
          <div class="top-right-controls">
            <button @click="toggleSubtitles" class="control-btn" title="Subtitles">
              <span class="control-icon">CC</span>
            </button>
            <button @click="toggleQualityMenu" class="control-btn" title="Quality">
              <span class="control-icon">HD</span>
            </button>
            <button @click="toggleFullscreen" class="control-btn" title="Fullscreen">
              <span class="control-icon">⛶</span>
            </button>
          </div>
        </div>

        <!-- Center Play Button -->
        <div class="center-controls">
          <button v-if="!isPlaying" @click="togglePlayPause" class="play-button">
            <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 5v10l8-5-8-5z"/>
            </svg>
          </button>
        </div>

        <!-- Bottom Controls -->
        <div class="bottom-controls">
          <div class="progress-container">
            <div class="time-display">{{ formatTime(currentTime) }}</div>
            <div class="progress-bar" @click="seekTo">
              <div class="progress-bg"></div>
              <div class="progress-buffer" :style="{ width: bufferPercentage + '%' }"></div>
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
              <div class="progress-thumb" :style="{ left: progressPercentage + '%' }"></div>
            </div>
            <div class="time-display">{{ formatTime(duration) }}</div>
          </div>
          
          <div class="control-buttons">
            <button @click="togglePlayPause" class="control-btn">
              <svg v-if="!isPlaying" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5v10l8-5-8-5z"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 4h3v12H5V4zm7 0h3v12h-3V4z"/>
              </svg>
            </button>
            
            <button @click="toggleMute" class="control-btn">
              <svg v-if="!isMuted" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L5.5 14H3a1 1 0 01-1-1V7a1 1 0 011-1h2.5l2.883-2.793a1 1 0 011.617.793z"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L5.5 14H3a1 1 0 01-1-1V7a1 1 0 011-1h2.5l2.883-2.793a1 1 0 011.617.793zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z"/>
              </svg>
            </button>
            
            <div class="volume-control">
              <input 
                type="range" 
                v-model="volume" 
                @input="changeVolume"
                min="0" 
                max="1" 
                step="0.1" 
                class="volume-slider"
              />
            </div>
            
            <div class="spacer"></div>
            
            <select v-model="playbackSpeed" @change="changePlaybackSpeed" class="speed-select">
              <option value="0.5">0.5x</option>
              <option value="0.75">0.75x</option>
              <option value="1">1x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Quality Menu -->
      <div v-if="showQualityMenu" class="quality-menu">
        <div class="menu-header">Video Quality</div>
        <div class="quality-options">
          <button 
            v-for="quality in availableQualities" 
            :key="quality.value"
            @click="selectQuality(quality.value)"
            :class="['quality-option', { 'active': currentQuality === quality.value }]"
          >
            <span class="quality-label">{{ quality.label }}</span>
            <span v-if="quality.value === 'auto'" class="quality-note">(Recommended)</span>
            <span v-if="currentQuality === quality.value" class="checkmark">✓</span>
          </button>
        </div>
      </div>

      <!-- Subtitle Menu -->
      <div v-if="showSubtitleMenu" class="subtitle-menu">
        <div class="menu-header">Subtitles</div>
        <div class="subtitle-options">
          <button @click="disableSubtitles" :class="{ active: selectedSubtitle === -1 }" class="subtitle-option">
            Off
          </button>
          <button 
            v-for="(subtitle, index) in subtitles" 
            :key="index"
            @click="selectSubtitle(index)"
            :class="{ active: selectedSubtitle === index }"
            class="subtitle-option"
          >
            {{ subtitle.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Subtitle {
  src: string
  label: string
  language: string
  default?: boolean
}

interface Props {
  videoSrc: string
  poster?: string
  subtitles?: Subtitle[]
  videoTitle?: string
  autoplay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitles: () => [],
  autoplay: false
})

const emit = defineEmits<{
  play: []
  pause: []
  ended: []
  timeupdate: [currentTime: number, duration: number]
  fullscreenchange: [isFullscreen: boolean]
}>()

// Refs
const videoElement = ref<HTMLVideoElement>()
const playerContainer = ref<HTMLDivElement>()
const showControls = ref(true)
const showQualityMenu = ref(false)
const showSubtitleMenu = ref(false)

// Video state
const isPlaying = ref(false)
const isMuted = ref(false)
const isLoading = ref(true)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const playbackSpeed = ref(1)
const selectedSubtitle = ref(-1)
const bufferPercentage = ref(0)

// Quality options
const currentQuality = ref('auto')
const availableQualities = ref([
  { value: 'auto', label: 'Auto' },
  { value: '1080p', label: '1080p HD' },
  { value: '720p', label: '720p HD' },
  { value: '480p', label: '480p' },
  { value: '360p', label: '360p' }
])

// Computed
const progressPercentage = computed(() => {
  return duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0
})

// Methods
const togglePlayPause = () => {
  if (!videoElement.value) return
  
  if (isPlaying.value) {
    videoElement.value.pause()
  } else {
    videoElement.value.play()
  }
}

const toggleMute = () => {
  if (!videoElement.value) return
  videoElement.value.muted = !videoElement.value.muted
  isMuted.value = videoElement.value.muted
}

const changeVolume = () => {
  if (!videoElement.value) return
  videoElement.value.volume = volume.value
  isMuted.value = volume.value === 0
}

const changePlaybackSpeed = () => {
  if (!videoElement.value) return
  videoElement.value.playbackRate = parseFloat(playbackSpeed.value.toString())
}

const seekTo = (event: MouseEvent) => {
  if (!videoElement.value || !duration.value) return
  
  const progressBar = event.currentTarget as HTMLElement
  const rect = progressBar.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percentage = clickX / rect.width
  const newTime = percentage * duration.value
  
  videoElement.value.currentTime = newTime
}

const toggleFullscreen = async () => {
  if (!playerContainer.value) return
  
  try {
    if (!document.fullscreenElement) {
      await playerContainer.value.requestFullscreen()
    } else {
      await document.exitFullscreen()
    }
  } catch (error) {
    console.error('Fullscreen error:', error)
  }
}

const toggleQualityMenu = () => {
  showQualityMenu.value = !showQualityMenu.value
  showSubtitleMenu.value = false
}

const toggleSubtitles = () => {
  showSubtitleMenu.value = !showSubtitleMenu.value
  showQualityMenu.value = false
}

const selectQuality = (quality: string) => {
  currentQuality.value = quality
  showQualityMenu.value = false
  console.log('Quality selected:', quality)
  // Here you would implement actual quality switching
}

const selectSubtitle = (index: number) => {
  selectedSubtitle.value = index
  showSubtitleMenu.value = false
  
  if (videoElement.value) {
    const tracks = videoElement.value.textTracks
    for (let i = 0; i < tracks.length; i++) {
      tracks[i].mode = i === index ? 'showing' : 'hidden'
    }
  }
}

const disableSubtitles = () => {
  selectedSubtitle.value = -1
  showSubtitleMenu.value = false
  
  if (videoElement.value) {
    const tracks = videoElement.value.textTracks
    for (let i = 0; i < tracks.length; i++) {
      tracks[i].mode = 'hidden'
    }
  }
}

const formatTime = (seconds: number): string => {
  if (!seconds || isNaN(seconds)) return '0:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// Event handlers
const onLoadedMetadata = () => {
  if (videoElement.value) {
    duration.value = videoElement.value.duration
    isLoading.value = false
  }
}

const onTimeUpdate = () => {
  if (videoElement.value) {
    currentTime.value = videoElement.value.currentTime
    emit('timeupdate', currentTime.value, duration.value)
  }
}

const onPlay = () => {
  isPlaying.value = true
  emit('play')
}

const onPause = () => {
  isPlaying.value = false
  emit('pause')
}

const onEnded = () => {
  isPlaying.value = false
  emit('ended')
}

const onWaiting = () => {
  isLoading.value = true
}

const onPlaying = () => {
  isLoading.value = false
}

const onProgress = () => {
  if (videoElement.value && videoElement.value.buffered.length > 0) {
    const buffered = videoElement.value.buffered.end(videoElement.value.buffered.length - 1)
    bufferPercentage.value = duration.value > 0 ? (buffered / duration.value) * 100 : 0
  }
}

const onError = (error: Event) => {
  console.error('Video error:', error)
  isLoading.value = false
}

// Auto-hide controls
let controlsTimeout: NodeJS.Timeout | null = null

const showControlsTemporarily = () => {
  showControls.value = true
  if (controlsTimeout) clearTimeout(controlsTimeout)
  controlsTimeout = setTimeout(() => {
    if (isPlaying.value) {
      showControls.value = false
    }
  }, 3000)
}

// Lifecycle
onMounted(() => {
  if (playerContainer.value) {
    playerContainer.value.addEventListener('mousemove', showControlsTemporarily)
    playerContainer.value.addEventListener('mouseleave', () => {
      if (isPlaying.value) {
        showControls.value = false
      }
    })
  }
  
  if (props.autoplay && videoElement.value) {
    videoElement.value.play()
  }
})

onUnmounted(() => {
  if (controlsTimeout) clearTimeout(controlsTimeout)
})
</script>

<style scoped>
.enhanced-video-player {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  opacity: 0.8;
}

.controls-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.7) 0%,
    transparent 20%,
    transparent 80%,
    rgba(0, 0, 0, 0.7) 100%
  );
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.controls-overlay.visible {
  opacity: 1;
  pointer-events: auto;
}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
}

.video-title {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.top-right-controls {
  display: flex;
  gap: 8px;
}

.center-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.play-button {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #000;
}

.play-button:hover {
  background: white;
  transform: scale(1.1);
}

.bottom-controls {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-display {
  color: white;
  font-size: 14px;
  min-width: 45px;
  text-align: center;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  position: relative;
  cursor: pointer;
}

.progress-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.progress-buffer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 3px;
  transition: width 0.2s ease;
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: #3b82f6;
  border-radius: 3px;
  transition: width 0.1s ease;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border: 2px solid white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: left 0.1s ease;
}

.control-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.control-icon {
  font-size: 16px;
  font-weight: bold;
}

.volume-control {
  display: flex;
  align-items: center;
}

.volume-slider {
  width: 80px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}

.spacer {
  flex: 1;
}

.speed-select {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.quality-menu,
.subtitle-menu {
  position: absolute;
  top: 60px;
  right: 16px;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 8px;
  padding: 8px;
  min-width: 200px;
  z-index: 10;
}

.menu-header {
  color: white;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 8px;
}

.quality-options,
.subtitle-options {
  display: flex;
  flex-direction: column;
}

.quality-option,
.subtitle-option {
  background: none;
  border: none;
  color: white;
  padding: 8px 12px;
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quality-option:hover,
.subtitle-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.quality-option.active,
.subtitle-option.active {
  background: #3b82f6;
}

.quality-label {
  font-weight: 500;
}

.quality-note {
  font-size: 12px;
  opacity: 0.7;
}

.checkmark {
  font-weight: bold;
}
</style>
