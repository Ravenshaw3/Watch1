<template>
  <div class="advanced-video-player">
    <div class="video-container" ref="videoContainer">
      <video
        ref="videoElement"
        :src="videoSrc"
        :poster="poster"
        class="video-element"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
        @play="onPlay"
        @pause="onPause"
        @click="togglePlayPause"
        @dblclick="toggleFullscreen"
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
        Your browser does not support the video tag.
      </video>

      <!-- Custom Controls Overlay -->
      <div 
        v-show="showControls" 
        class="controls-overlay"
        @mousemove="showControlsTemporarily"
        @mouseleave="hideControlsAfterDelay"
      >
        <!-- Top Controls -->
        <div class="controls-top">
          <div class="controls-left">
            <button @click="togglePictureInPicture" class="control-btn" title="Picture-in-Picture">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </button>
            <button @click="toggleFullscreen" class="control-btn" title="Fullscreen">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3z"/>
              </svg>
            </button>
          </div>
          <div class="controls-right">
            <button @click="toggleSubtitles" class="control-btn" title="Subtitles">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
            </button>
            <div class="speed-control">
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

        <!-- Center Play Button -->
        <div class="controls-center">
          <button @click="togglePlayPause" class="play-button">
            <svg v-if="!isPlaying" class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 5v10l8-5-8-5z"/>
            </svg>
            <svg v-else class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 4h3v12H5V4zm7 0h3v12h-3V4z"/>
            </svg>
          </button>
        </div>

        <!-- Bottom Controls -->
        <div class="controls-bottom">
          <div class="progress-container">
            <div class="time-display">{{ formatTime(currentTime) }}</div>
            <div class="progress-bar" @click="seekTo">
              <div class="progress-bg"></div>
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
              <div class="progress-thumb" :style="{ left: progressPercentage + '%' }"></div>
            </div>
            <div class="time-display">{{ formatTime(duration) }}</div>
          </div>
          
          <div class="controls-bottom-right">
            <button @click="toggleMute" class="control-btn" title="Mute">
              <svg v-if="!isMuted" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L5.5 14H3a1 1 0 01-1-1V7a1 1 0 011-1h2.5l2.883-2.793a1 1 0 011.617.793zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z"/>
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
          </div>
        </div>
      </div>
    </div>

    <!-- Subtitle Menu -->
    <div v-if="showSubtitleMenu" class="subtitle-menu">
      <div class="subtitle-options">
        <button 
          v-for="(subtitle, index) in subtitles" 
          :key="index"
          @click="selectSubtitle(index)"
          :class="{ active: selectedSubtitle === index }"
          class="subtitle-option"
        >
          {{ subtitle.label }}
        </button>
        <button @click="disableSubtitles" class="subtitle-option">Off</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

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
  autoplay?: boolean
  loop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitles: () => [],
  autoplay: false,
  loop: false
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
const videoContainer = ref<HTMLDivElement>()
const showControls = ref(true)
const showSubtitleMenu = ref(false)

// Video state
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const playbackSpeed = ref(1)
const selectedSubtitle = ref(-1)

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
  if (!videoContainer.value) return
  
  try {
    if (!document.fullscreenElement) {
      await videoContainer.value.requestFullscreen()
    } else {
      await document.exitFullscreen()
    }
  } catch (error) {
    console.error('Fullscreen error:', error)
  }
}

const togglePictureInPicture = async () => {
  if (!videoElement.value) return
  
  try {
    if (document.pictureInPictureElement) {
      await document.exitPictureInPicture()
    } else {
      await videoElement.value.requestPictureInPicture()
    }
  } catch (error) {
    console.error('Picture-in-Picture error:', error)
  }
}

const toggleSubtitles = () => {
  showSubtitleMenu.value = !showSubtitleMenu.value
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

const formatTime = (time: number): string => {
  const hours = Math.floor(time / 3600)
  const minutes = Math.floor((time % 3600) / 60)
  const seconds = Math.floor(time % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const showControlsTemporarily = () => {
  showControls.value = true
  hideControlsAfterDelay()
}

const hideControlsAfterDelay = () => {
  setTimeout(() => {
    if (isPlaying.value) {
      showControls.value = false
    }
  }, 3000)
}

// Event handlers
const onLoadedMetadata = () => {
  if (!videoElement.value) return
  duration.value = videoElement.value.duration
  volume.value = videoElement.value.volume
}

const onTimeUpdate = () => {
  if (!videoElement.value) return
  currentTime.value = videoElement.value.currentTime
  emit('timeupdate', currentTime.value, duration.value)
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

// Lifecycle
onMounted(() => {
  if (props.autoplay && videoElement.value) {
    videoElement.value.play()
  }
  
  // Set up fullscreen change listener
  document.addEventListener('fullscreenchange', () => {
    emit('fullscreenchange', !!document.fullscreenElement)
  })
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', () => {})
})

// Watch for subtitle changes
watch(() => props.subtitles, (newSubtitles) => {
  if (newSubtitles.length > 0) {
    selectedSubtitle.value = newSubtitles.findIndex(sub => sub.default) || 0
  }
}, { immediate: true })
</script>

<style scoped>
.advanced-video-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
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
  padding: 1rem;
  transition: opacity 0.3s ease;
}

.controls-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controls-left,
.controls-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-btn {
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.control-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

.speed-select {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.controls-center {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
}

.play-button {
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  padding: 1rem;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.play-button:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: scale(1.1);
}

.controls-bottom {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.time-display {
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 3rem;
  text-align: center;
}

.progress-bar {
  position: relative;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  cursor: pointer;
  flex: 1;
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #3b82f6;
  border-radius: 2px;
  transition: width 0.1s ease;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  background: #3b82f6;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.progress-bar:hover .progress-thumb {
  opacity: 1;
}

.controls-bottom-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.volume-slider {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  appearance: none;
  width: 12px;
  height: 12px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}

.subtitle-menu {
  position: absolute;
  top: 4rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 8px;
  padding: 0.5rem;
  min-width: 150px;
}

.subtitle-options {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.subtitle-option {
  background: none;
  border: none;
  color: white;
  padding: 0.5rem;
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.subtitle-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.subtitle-option.active {
  background: #3b82f6;
}

/* Hide controls when not interacting */
.advanced-video-player:not(:hover) .controls-overlay {
  opacity: 0;
}

.advanced-video-player:hover .controls-overlay {
  opacity: 1;
}
</style>
