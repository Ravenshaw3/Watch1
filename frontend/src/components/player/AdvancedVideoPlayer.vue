<template>
  <div class="advanced-video-player">
    <div class="video-container" ref="videoContainer">
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
        @loadstart="onLoadStart"
        @loadeddata="onLoadedData"
        @canplay="onCanPlay"
        @canplaythrough="onCanPlayThrough"
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
            <button 
              @click="togglePictureInPicture" 
              :disabled="!pipSupported"
              :class="['control-btn', { 'pip-active': isPictureInPicture, 'pip-disabled': !pipSupported }]" 
              :title="pipSupported ? (isPictureInPicture ? 'Exit Picture-in-Picture' : 'Enter Picture-in-Picture') : 'Picture-in-Picture not supported'"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="!isPictureInPicture" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                <path v-else d="M2 3a1 1 0 011-1h14a1 1 0 011 1v11a1 1 0 01-1 1H3a1 1 0 01-1-1V3zm12 1H4v9h10V4zm-8 7a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1H7a1 1 0 01-1-1v-2z"/>
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
            <button 
              @click="toggleAudioTracks" 
              v-if="audioTracks.length > 1"
              class="control-btn" 
              title="Audio Tracks"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.369 4.369 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
              </svg>
            </button>
            <div class="quality-control">
              <button @click="toggleQualityMenu" class="control-btn" title="Video Quality">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
              </button>
            </div>
            <div class="speed-control">
              <select v-model="playbackSpeed" @change="changePlaybackSpeed" class="speed-select" title="Playback Speed">
                <option value="0.25">0.25x</option>
                <option value="0.5">0.5x</option>
                <option value="0.75">0.75x</option>
                <option value="1">1x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
                <option value="1.75">1.75x</option>
                <option value="2">2x</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Center Play Button -->
        <div class="controls-center">
          <!-- Loading/Buffering Indicator -->
          <div v-if="isBuffering || loadingState === 'loading'" class="loading-indicator">
            <div class="loading-spinner"></div>
            <span class="loading-text">
              {{ loadingState === 'loading' ? 'Loading...' : 'Buffering...' }}
            </span>
          </div>
          
          <!-- Error Indicator -->
          <div v-else-if="loadingState === 'error'" class="error-indicator">
            <svg class="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <span class="error-text">Playback Error</span>
          </div>
          
          <!-- Normal Play Button -->
          <button v-else @click="togglePlayPause" class="play-button">
            <svg v-if="!isPlaying" class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 5v10l8-5-8-5z"/>
            </svg>
            <svg v-else class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 4h3v12H5V4zm7 0h3v12h-3V4z"/>
            </svg>
          </button>
          
          <!-- Skip buttons for series/episodes -->
          <div class="skip-controls" v-if="showSkipControls && loadingState === 'ready'">
            <button @click="skipBackward" class="skip-button" title="Previous Episode">
              <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8.445 14.832A1 1 0 0010 14v-2.798l5.445 3.63A1 1 0 0017 14V6a1 1 0 00-1.555-.832L10 8.798V6a1 1 0 00-1.555-.832l-6 4a1 1 0 000 1.664l6 4z"/>
              </svg>
            </button>
            <button @click="skipForward" class="skip-button" title="Next Episode">
              <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798L4.555 5.168z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Bottom Controls -->
        <div class="controls-bottom">
          <div class="progress-container">
            <div class="time-display">{{ formatTime(currentTime) }}</div>
            <div class="progress-bar" @click="seekTo" @mousemove="showPreview" @mouseleave="hidePreview">
              <div class="progress-bg"></div>
              <div class="progress-buffer" :style="{ width: bufferPercentage + '%' }"></div>
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
              
              <!-- Chapter markers -->
              <div 
                v-for="chapter in chapters" 
                :key="chapter.time"
                class="chapter-marker"
                :style="{ left: (chapter.time / duration * 100) + '%' }"
                :title="chapter.title"
              ></div>
              
              <div class="progress-thumb" :style="{ left: progressPercentage + '%' }"></div>
              
              <!-- Preview tooltip -->
              <div 
                v-if="showPreviewTooltip" 
                class="progress-preview"
                :style="{ left: previewPosition + 'px' }"
              >
                <div class="preview-time">{{ formatTime(previewTime) }}</div>
              </div>
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
      <div class="subtitle-header">
        <h3>Subtitles</h3>
        <button @click="openSubtitleSettings" class="settings-btn" title="Subtitle Settings">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </button>
      </div>
      <div class="subtitle-options">
        <button @click="disableSubtitles" :class="{ active: selectedSubtitle === -1 }" class="subtitle-option">
          <span class="option-text">Off</span>
        </button>
        <button 
          v-for="(subtitle, index) in subtitles" 
          :key="index"
          @click="selectSubtitle(index)"
          :class="{ active: selectedSubtitle === index }"
          class="subtitle-option"
        >
          <span class="option-text">{{ subtitle.label }}</span>
          <span class="option-format">{{ getSubtitleFormat(subtitle.src) }}</span>
        </button>
      </div>
    </div>

    <!-- Subtitle Settings Menu -->
    <div v-if="showSubtitleSettings" class="subtitle-settings-menu">
      <div class="settings-header">
        <h3>Subtitle Settings</h3>
        <button @click="closeSubtitleSettings" class="close-btn">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
      <div class="settings-content">
        <div class="setting-group">
          <label class="setting-label">Font Size</label>
          <select v-model="subtitleSettings.fontSize" @change="applySubtitleSettings" class="setting-select">
            <option value="12px">Small</option>
            <option value="16px">Medium</option>
            <option value="20px">Large</option>
            <option value="24px">Extra Large</option>
          </select>
        </div>
        
        <div class="setting-group">
          <label class="setting-label">Font Color</label>
          <select v-model="subtitleSettings.color" @change="applySubtitleSettings" class="setting-select">
            <option value="white">White</option>
            <option value="yellow">Yellow</option>
            <option value="cyan">Cyan</option>
            <option value="red">Red</option>
            <option value="green">Green</option>
          </select>
        </div>
        
        <div class="setting-group">
          <label class="setting-label">Background</label>
          <select v-model="subtitleSettings.background" @change="applySubtitleSettings" class="setting-select">
            <option value="none">None</option>
            <option value="black">Black</option>
            <option value="semi-transparent">Semi-transparent</option>
          </select>
        </div>
        
        <div class="setting-group">
          <label class="setting-label">Position</label>
          <select v-model="subtitleSettings.position" @change="applySubtitleSettings" class="setting-select">
            <option value="bottom">Bottom</option>
            <option value="top">Top</option>
            <option value="middle">Middle</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Audio Track Menu -->
    <div v-if="showAudioMenu" class="audio-menu">
      <div class="audio-options">
        <button 
          v-for="(track, index) in audioTracks" 
          :key="index"
          @click="selectAudioTrack(index)"
          :class="{ active: selectedAudioTrack === index }"
          class="audio-option"
        >
          {{ track.label }}
        </button>
      </div>
    </div>

    <!-- Quality Selection Menu -->
    <div v-if="showQualityMenu" class="quality-menu">
      <div class="quality-header">
        <h3>Video Quality</h3>
        <span class="quality-info">{{ getCurrentQualityInfo() }}</span>
      </div>
      <div class="quality-options">
        <button 
          v-for="quality in availableQualities" 
          :key="quality.id"
          @click="selectQuality(quality)"
          :class="{ active: selectedQuality?.id === quality.id }"
          class="quality-option"
        >
          <div class="quality-main">
            <span class="quality-label">{{ quality.label }}</span>
            <span class="quality-resolution">{{ quality.resolution }}</span>
          </div>
          <div class="quality-meta">
            <span class="quality-bitrate">{{ quality.bitrate }}</span>
            <span v-if="quality.id === 'auto'" class="quality-auto">Auto</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Auto-Advance Countdown -->
    <div v-if="showCountdown" class="countdown-overlay">
      <div class="countdown-content">
        <div class="countdown-header">
          <h3>Up Next</h3>
        </div>
        <div class="countdown-actions">
          <button @click="cancelCountdown" class="countdown-btn cancel">Cancel</button>
          <button @click="playNext" class="countdown-btn play">Play Now</button>
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
  autoplay?: boolean
  loop?: boolean
  autoAdvance?: boolean
  nextVideoTitle?: string
  countdownDuration?: number
  showSkipControls?: boolean
  hasPreviousEpisode?: boolean
  hasNextEpisode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitles: () => [],
  autoplay: false,
  loop: false,
  autoAdvance: false,
  nextVideoTitle: '',
  countdownDuration: 10
})

const emit = defineEmits<{
  play: []
  pause: []
  ended: []
  timeupdate: [currentTime: number, duration: number]
  fullscreenchange: [isFullscreen: boolean]
  nextVideo: []
  previousVideo: []
  skipBackward: []
  skipForward: []
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
const isPictureInPicture = ref(false)
const pipSupported = ref(false)
const audioTracks = ref<any[]>([])
const selectedAudioTrack = ref(0)
const showAudioMenu = ref(false)
const showCountdown = ref(false)
const countdownTimer = ref(0)
const countdownInterval = ref<NodeJS.Timeout | null>(null)

// Enhanced progress bar features
const bufferPercentage = ref(0)
const chapters = ref<Array<{time: number, title: string}>>([])
const showPreviewTooltip = ref(false)
const previewPosition = ref(0)
const previewTime = ref(0)

// Subtitle settings
const showSubtitleSettings = ref(false)
const subtitleSettings = ref({
  fontSize: '16px',
  color: 'white',
  background: 'semi-transparent',
  position: 'bottom'
})

// Streaming performance tracking
const loadingState = ref<'loading' | 'buffering' | 'ready' | 'error'>('loading')
const networkState = ref(0)
const readyState = ref(0)
const isBuffering = ref(false)
const loadStartTime = ref(0)
const firstPlayTime = ref(0)

// Quality selection
const showQualityMenu = ref(false)
const selectedQuality = ref<QualityOption | null>(null)
const availableQualities = ref<QualityOption[]>([
  { id: 'auto', label: 'Auto', resolution: 'Adaptive', bitrate: 'Variable', url: '' },
  { id: '1080p', label: '1080p', resolution: '1920x1080', bitrate: '8 Mbps', url: '' },
  { id: '720p', label: '720p', resolution: '1280x720', bitrate: '5 Mbps', url: '' },
  { id: '480p', label: '480p', resolution: '854x480', bitrate: '2.5 Mbps', url: '' },
  { id: '360p', label: '360p', resolution: '640x360', bitrate: '1 Mbps', url: '' }
])

interface QualityOption {
  id: string
  label: string
  resolution: string
  bitrate: string
  url: string
}

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
  if (!videoElement.value || !pipSupported.value) {
    console.warn('Picture-in-Picture not supported')
    return
  }
  
  try {
    if (isPictureInPicture.value) {
      await document.exitPictureInPicture()
    } else {
      // Ensure video is playing for better PiP experience
      if (!isPlaying.value) {
        await videoElement.value.play()
      }
      await videoElement.value.requestPictureInPicture()
    }
  } catch (error: any) {
    console.error('Picture-in-Picture error:', error)
    
    // Provide user feedback for common errors
    if (error?.name === 'InvalidStateError') {
      console.warn('Picture-in-Picture failed: Video not ready or already in PiP')
    } else if (error?.name === 'NotSupportedError') {
      console.warn('Picture-in-Picture not supported by this browser')
    } else if (error?.name === 'NotAllowedError') {
      console.warn('Picture-in-Picture blocked by user or policy')
    }
  }
}

// Picture-in-Picture event handlers
const onEnterPictureInPicture = () => {
  isPictureInPicture.value = true
  console.log('Entered Picture-in-Picture mode')
}

const onLeavePictureInPicture = () => {
  isPictureInPicture.value = false
  console.log('Left Picture-in-Picture mode')
}

// Check Picture-in-Picture support
const checkPiPSupport = () => {
  pipSupported.value = 'pictureInPictureEnabled' in document && document.pictureInPictureEnabled
  console.log('Picture-in-Picture supported:', pipSupported.value)
}

const toggleSubtitles = () => {
  showSubtitleMenu.value = !showSubtitleMenu.value
}

const toggleAudioTracks = () => {
  showAudioMenu.value = !showAudioMenu.value
}

const selectAudioTrack = (index: number) => {
  selectedAudioTrack.value = index
  showAudioMenu.value = false
  
  if (videoElement.value) {
    // Note: HTML5 video doesn't natively support multiple audio tracks
    // This would typically require a media library like HLS.js or Dash.js
    console.log(`Selected audio track ${index}:`, audioTracks.value[index])
  }
}

const detectAudioTracks = () => {
  if (!videoElement.value) return
  
  // For now, we'll simulate audio track detection
  // In a real implementation, this would use HLS.js or similar
  const tracks = []
  
  // Check if the video has multiple audio tracks (requires HLS/DASH)
  const videoEl = videoElement.value as any
  if (videoEl.audioTracks && videoEl.audioTracks.length > 0) {
    for (let i = 0; i < videoEl.audioTracks.length; i++) {
      const track = videoEl.audioTracks[i]
      tracks.push({
        id: track.id || `track-${i}`,
        label: track.label || `Audio Track ${i + 1}`,
        language: track.language || 'unknown',
        enabled: track.enabled
      })
    }
  } else {
    // Default single audio track
    tracks.push({
      id: 'default',
      label: 'Default Audio',
      language: 'unknown',
      enabled: true
    })
  }
  
  audioTracks.value = tracks
  console.log('Detected audio tracks:', tracks)
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
  
  // Detect available audio tracks
  detectAudioTracks()
}

const onTimeUpdate = () => {
  if (!videoElement.value) return
  currentTime.value = videoElement.value.currentTime
  updateBufferProgress()
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
  
  // Start auto-advance countdown if enabled
  if (props.autoAdvance && props.nextVideoTitle) {
    startCountdown()
  }
}

const startCountdown = () => {
  showCountdown.value = true
  countdownTimer.value = props.countdownDuration
  
  countdownInterval.value = setInterval(() => {
    countdownTimer.value--
    
    if (countdownTimer.value <= 0) {
      clearInterval(countdownInterval.value!)
      showCountdown.value = false
      emit('nextVideo')
    }
  }, 1000)
}

const cancelCountdown = () => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
  showCountdown.value = false
  countdownTimer.value = 0
}

const playNext = () => {
  cancelCountdown()
  emit('nextVideo')
}

// Skip controls for series/episodes
const skipBackward = () => {
  emit('skipBackward')
  emit('previousVideo')
}

const skipForward = () => {
  emit('skipForward')
  emit('nextVideo')
}

// Progress bar preview methods
const showPreview = (event: MouseEvent) => {
  if (!duration.value) return
  
  const progressBar = event.currentTarget as HTMLElement
  const rect = progressBar.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percentage = clickX / rect.width
  
  previewTime.value = percentage * duration.value
  previewPosition.value = clickX
  showPreviewTooltip.value = true
}

const hidePreview = () => {
  showPreviewTooltip.value = false
}

// Update buffer progress
const updateBufferProgress = () => {
  if (!videoElement.value || !duration.value) return
  
  const buffered = videoElement.value.buffered
  if (buffered.length > 0) {
    const bufferedEnd = buffered.end(buffered.length - 1)
    bufferPercentage.value = (bufferedEnd / duration.value) * 100
  }
}

// Subtitle changes handled in onMounted
</script>

<style scoped>
.advanced-video-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  showSubtitleSettings.value = false
}

const applySubtitleSettings = () => {
  if (!videoElement.value) return
  
  // Apply custom subtitle styling
  const style = document.createElement('style')
  style.id = 'subtitle-custom-styles'
  
  // Remove existing custom styles
  const existingStyle = document.getElementById('subtitle-custom-styles')
  if (existingStyle) {
    existingStyle.remove()
  }
  
  let css = `
    video::cue {
      font-size: ${subtitleSettings.value.fontSize} !important;
      color: ${subtitleSettings.value.color} !important;
  `
  
  // Background styling
  if (subtitleSettings.value.background === 'black') {
    css += 'background-color: black !important;'
  } else if (subtitleSettings.value.background === 'semi-transparent') {
    css += 'background-color: rgba(0, 0, 0, 0.7) !important;'
  }
  
  // Position styling
  if (subtitleSettings.value.position === 'top') {
    css += 'line-height: 1.2; position: absolute; top: 10%;'
  } else if (subtitleSettings.value.position === 'middle') {
    css += 'line-height: 1.2; position: absolute; top: 45%;'
  }
  
  css += '}'
  
  style.textContent = css
  document.head.appendChild(style)
  
  // Save settings to localStorage
  localStorage.setItem('subtitle_settings', JSON.stringify(subtitleSettings.value))
}

const getSubtitleFormat = (src: string): string => {
  const url = new URL(src, window.location.origin)
  const filename = url.pathname.split('/').pop() || ''
  const extension = filename.split('.').pop()?.toUpperCase()
  return extension || 'Unknown'
}

// Streaming performance event handlers
const onLoadStart = () => {
  loadStartTime.value = Date.now()
  loadingState.value = 'loading'
  console.log('Video load started')
}

const onLoadedData = () => {
  if (!videoElement.value) return
  readyState.value = videoElement.value.readyState
  networkState.value = videoElement.value.networkState
  console.log('Video data loaded, readyState:', readyState.value)
}

const onCanPlay = () => {
  loadingState.value = 'ready'
  const loadTime = Date.now() - loadStartTime.value
  console.log(`Video can start playing (load time: ${loadTime}ms)`)
  
  // Preload a bit more for smooth playback
  if (videoElement.value && !isPlaying.value) {
    videoElement.value.currentTime = 0.1
    videoElement.value.currentTime = 0
  }
}

const onCanPlayThrough = () => {
  console.log('Video can play through without buffering')
  loadingState.value = 'ready'
}

const onWaiting = () => {
  isBuffering.value = true
  loadingState.value = 'buffering'
  console.log('Video is waiting for data (buffering)')
}

const onPlaying = () => {
  isBuffering.value = false
  loadingState.value = 'ready'
  
  if (firstPlayTime.value === 0) {
    firstPlayTime.value = Date.now() - loadStartTime.value
    console.log(`First play achieved in ${firstPlayTime.value}ms`)
  }
}

const onProgress = () => {
  updateBufferProgress()
  
  // Log buffering progress occasionally
  if (Math.random() < 0.1) { // 10% chance to log
    console.log(`Buffer: ${bufferPercentage.value.toFixed(1)}%`)
  }
}

const onError = (event: Event) => {
  loadingState.value = 'error'
  const target = event.target as HTMLVideoElement
  const error = target.error
  
  if (error) {
    console.error('Video error:', {
      code: error.code,
      message: error.message,
      networkState: target.networkState,
      readyState: target.readyState
    })
    
    // Attempt recovery for network errors
    if (error.code === MediaError.MEDIA_ERR_NETWORK) {
      console.log('Attempting to recover from network error...')
      setTimeout(() => {
        if (videoElement.value) {
          videoElement.value.load()
        }
      }, 2000)
    }
  }
}

// Quality selection methods
const toggleQualityMenu = () => {
  showQualityMenu.value = !showQualityMenu.value
  showAudioMenu.value = false
  showSubtitleMenu.value = false
}

const selectQuality = (quality: QualityOption) => {
  const currentTime = videoElement.value?.currentTime || 0
  const wasPlaying = isPlaying.value
  
  selectedQuality.value = quality
  showQualityMenu.value = false
  
  if (quality.id === 'auto') {
    // For auto quality, use the original source
    console.log('Selected auto quality - using adaptive streaming')
  } else {
    // For specific qualities, we would need different source URLs
    // For now, we'll simulate quality selection
    console.log(`Selected quality: ${quality.label} (${quality.resolution})`)
  }
  
  // Resume playback at the same position
  if (videoElement.value) {
    videoElement.value.currentTime = currentTime
    if (wasPlaying) {
      videoElement.value.play()
    }
  }
}

const getCurrentQualityInfo = (): string => {
  if (!selectedQuality.value) {
    return 'Auto'
  }
  return `${selectedQuality.value.label} • ${selectedQuality.value.resolution}`
}

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  if (!videoElement.value) return
  
  // Prevent default for our handled keys
  const handledKeys = ['Space', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'KeyF', 'KeyM', 'KeyP', 'Comma', 'Period']
  if (handledKeys.includes(event.code)) {
    event.preventDefault()
  }
  
  switch (event.code) {
    case 'Space':
      togglePlayPause()
      break
    case 'ArrowLeft':
      // Seek backward 10 seconds
      videoElement.value.currentTime = Math.max(0, videoElement.value.currentTime - 10)
      break
    case 'ArrowRight':
      // Seek forward 10 seconds
      videoElement.value.currentTime = Math.min(duration.value, videoElement.value.currentTime + 10)
      break
    case 'ArrowUp':
      // Volume up
      volume.value = Math.min(1, volume.value + 0.1)
      changeVolume()
      break
    case 'ArrowDown':
      // Volume down
      volume.value = Math.max(0, volume.value - 0.1)
      changeVolume()
      break
    case 'KeyF':
      toggleFullscreen()
      break
    case 'KeyM':
      toggleMute()
      break
    case 'KeyP':
      togglePictureInPicture()
      break
    case 'Comma':
      // Decrease speed
      const currentSpeedIndex = speedOptions.indexOf(playbackSpeed.value)
      if (currentSpeedIndex > 0) {
        playbackSpeed.value = speedOptions[currentSpeedIndex - 1]
        changePlaybackSpeed()
      }
      break
    case 'Period':
      // Increase speed
      const currentSpeedIndexInc = speedOptions.indexOf(playbackSpeed.value)
      if (currentSpeedIndexInc < speedOptions.length - 1) {
        playbackSpeed.value = speedOptions[currentSpeedIndexInc + 1]
        changePlaybackSpeed()
      }
      break
  }
}

const speedOptions = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]

// Lifecycle
onMounted(() => {
  if (props.autoplay && videoElement.value) {
    videoElement.value.play()
  }
  
  // Check Picture-in-Picture support
  checkPiPSupport()
  
  // Initialize default quality
  selectedQuality.value = availableQualities.value[0] // Auto
  
  // Load saved subtitle settings
  const savedSettings = localStorage.getItem('subtitle_settings')
  if (savedSettings) {
    try {
      subtitleSettings.value = JSON.parse(savedSettings)
      applySubtitleSettings()
    } catch (error) {
      console.error('Failed to load subtitle settings:', error)
    }
  }
  
  // Set up event listeners
  document.addEventListener('fullscreenchange', () => {
    emit('fullscreenchange', !!document.fullscreenElement)
  })
  
  document.addEventListener('keydown', handleKeydown)
  
  // Picture-in-Picture event listeners
  if (videoElement.value) {
    videoElement.value.addEventListener('enterpictureinpicture', onEnterPictureInPicture)
    videoElement.value.addEventListener('leavepictureinpicture', onLeavePictureInPicture)
  }
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', () => {})
  document.removeEventListener('keydown', handleKeydown)
  
  // Clean up Picture-in-Picture event listeners
  if (videoElement.value) {
    videoElement.value.removeEventListener('enterpictureinpicture', onEnterPictureInPicture)
    videoElement.value.removeEventListener('leavepictureinpicture', onLeavePictureInPicture)
  }
  
  // Clean up countdown interval
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
  }
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

.control-btn.pip-active {
  background: #3b82f6;
  color: white;
}

.control-btn.pip-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.pip-disabled:hover {
  background: rgba(0, 0, 0, 0.5);
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
  gap: 1rem;
}

.skip-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.skip-button {
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  padding: 0.75rem;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skip-button:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: scale(1.05);
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: white;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 1rem;
  font-weight: 500;
}

.error-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #ef4444;
}

.error-text {
  font-size: 1rem;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.progress-buffer {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.chapter-marker {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 8px;
  background: #fbbf24;
  border-radius: 1px;
  cursor: pointer;
}

.progress-preview {
  position: absolute;
  bottom: 20px;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  pointer-events: none;
  z-index: 10;
}

.progress-preview::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.9);
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
  min-width: 200px;
  max-height: 300px;
  overflow-y: auto;
}

.subtitle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 0.5rem;
}

.subtitle-header h3 {
  color: white;
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.settings-btn {
  background: none;
  border: none;
  color: white;
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.1);
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-text {
  font-weight: 500;
}

.option-format {
  font-size: 0.75rem;
  color: #9ca3af;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.subtitle-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.subtitle-option.active {
  background: #3b82f6;
}

.subtitle-settings-menu {
  position: absolute;
  top: 4rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.95);
  border-radius: 8px;
  padding: 1rem;
  min-width: 250px;
  max-height: 400px;
  overflow-y: auto;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.settings-header h3 {
  color: white;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-label {
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.setting-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.setting-select option {
  background: #1f2937;
  color: white;
}

.audio-menu {
  position: absolute;
  top: 4rem;
  right: 5rem;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 8px;
  padding: 0.5rem;
  min-width: 150px;
}

.audio-options {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.audio-option {
  background: none;
  border: none;
  color: white;
  padding: 0.5rem;
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.audio-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.audio-option.active {
  background: #3b82f6;
}

.quality-menu {
  position: absolute;
  top: 4rem;
  right: 9rem;
  background: rgba(0, 0, 0, 0.95);
  border-radius: 8px;
  padding: 1rem;
  min-width: 280px;
  max-height: 400px;
  overflow-y: auto;
}

.quality-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.quality-header h3 {
  color: white;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.quality-info {
  color: #9ca3af;
  font-size: 0.875rem;
}

.quality-options {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.quality-option {
  background: none;
  border: none;
  color: white;
  padding: 0.75rem;
  text-align: left;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quality-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.quality-option.active {
  background: #3b82f6;
}

.quality-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.quality-label {
  font-weight: 600;
  font-size: 0.875rem;
}

.quality-resolution {
  font-size: 0.75rem;
  color: #d1d5db;
}

.quality-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.quality-bitrate {
  font-size: 0.75rem;
  color: #9ca3af;
}

.quality-auto {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
}

.countdown-overlay {
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

.countdown-content {
  background: rgba(0, 0, 0, 0.85);
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  min-width: 300px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.countdown-header {
{{ ... }}
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.countdown-header h3 {
  color: white;
  margin: 0;
  font-size: 1.25rem;
}

.countdown-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.countdown-close:hover {
  color: #ccc;
}

.countdown-info {
  color: white;
}

.next-video-title {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: #e5e7eb;
}

.countdown-timer {
  margin-bottom: 1.5rem;
}

.countdown-circle {
  width: 80px;
  height: 80px;
  border: 3px solid #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  animation: countdown-pulse 1s ease-in-out infinite;
}

.countdown-number {
  font-size: 2rem;
  font-weight: bold;
  color: #3b82f6;
}

.countdown-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.countdown-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.countdown-btn.cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.countdown-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.countdown-btn.play {
  background: #3b82f6;
  color: white;
}

.countdown-btn.play:hover {
  background: #2563eb;
}

@keyframes countdown-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* Hide controls when not interacting */
.advanced-video-player:not(:hover) .controls-overlay {
  opacity: 0;
}

.advanced-video-player:hover .controls-overlay {
  opacity: 1;
}
</style>
