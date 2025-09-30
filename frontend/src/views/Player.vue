<template>
  <div class="min-h-screen bg-black">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p class="text-white">Loading media...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center min-h-screen">
      <div class="text-center text-white">
        <ExclamationTriangleIcon class="h-16 w-16 mx-auto mb-4 text-red-500" />
        <h2 class="text-xl font-bold mb-2">Media Not Found</h2>
        <p class="text-gray-300 mb-6">{{ error }}</p>
        <router-link to="/library" class="btn-primary">
          Back to Library
        </router-link>
      </div>
    </div>

    <!-- Media Player -->
    <div v-else-if="media" class="relative">
      <!-- Video Player -->
      <VideoPlayer
        v-if="isVideoContent"
        :media="media"
        :autoplay="true"
        :show-custom-controls="true"
        :show-info="true"
        @play="onPlay"
        @pause="onPause"
        @ended="onEnded"
        @error="onPlayerError"
      />

      <!-- Audio Player -->
      <AudioPlayer
        v-else-if="isAudioContent"
        :media="media"
        :playlist="relatedMedia"
        :autoplay="true"
        :show-waveform="true"
        @play="onPlay"
        @pause="onPause"
        @ended="onEnded"
        @error="onPlayerError"
        @track-changed="onTrackChanged"
      />

      <!-- Image Viewer -->
      <div v-else-if="isImageContent" class="image-viewer">
        <div class="flex items-center justify-center min-h-screen p-4">
          <div class="max-w-full max-h-full">
            <img
              :src="mediaUrl"
              :alt="media.title || media.filename"
              class="max-w-full max-h-screen object-contain"
              @error="onImageError"
            />
          </div>
        </div>
        
        <!-- Image Controls -->
        <div class="absolute top-4 right-4 flex space-x-2">
          <button @click="downloadMedia" class="control-btn">
            <ArrowDownTrayIcon class="h-6 w-6" />
          </button>
          <button @click="toggleFullscreen" class="control-btn">
            <ArrowsPointingOutIcon class="h-6 w-6" />
          </button>
        </div>
      </div>

      <!-- Document Viewer -->
      <div v-else class="document-viewer">
        <div class="flex items-center justify-center min-h-screen p-8">
          <div class="text-center text-white">
            <DocumentIcon class="h-24 w-24 mx-auto mb-4 text-gray-400" />
            <h2 class="text-2xl font-bold mb-2">{{ media.title || media.filename }}</h2>
            <p class="text-gray-300 mb-6">This file type is not supported for preview</p>
            <button @click="downloadMedia" class="btn-primary">
              <ArrowDownTrayIcon class="h-5 w-5 mr-2" />
              Download File
            </button>
          </div>
        </div>
      </div>

      <!-- Player Controls Overlay -->
      <div class="absolute top-4 left-4 flex items-center space-x-4 z-50">
        <!-- Back Button -->
        <button @click="goBack" class="control-btn">
          <ArrowLeftIcon class="h-6 w-6" />
        </button>

        <!-- Media Info -->
        <div class="text-white">
          <h1 class="text-lg font-semibold">{{ media.title || media.filename }}</h1>
          <p class="text-sm text-gray-300 capitalize">{{ media.category }}</p>
        </div>
      </div>

      <!-- Additional Controls -->
      <div class="absolute top-4 right-4 flex items-center space-x-2 z-50">
        <!-- Add to Playlist -->
        <button @click="showAddToPlaylist = true" class="control-btn" title="Add to Playlist">
          <PlusIcon class="h-6 w-6" />
        </button>

        <!-- Share -->
        <button @click="shareMedia" class="control-btn" title="Share">
          <ShareIcon class="h-6 w-6" />
        </button>

        <!-- Download -->
        <button @click="downloadMedia" class="control-btn" title="Download">
          <ArrowDownTrayIcon class="h-6 w-6" />
        </button>

        <!-- Settings -->
        <button @click="showSettings = true" class="control-btn" title="Settings">
          <CogIcon class="h-6 w-6" />
        </button>
      </div>

      <!-- Related Media Sidebar -->
      <div
        v-if="showRelated && relatedMedia.length > 0"
        class="absolute right-0 top-0 bottom-0 w-80 bg-black bg-opacity-90 p-4 overflow-y-auto"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-white font-semibold">Related Media</h3>
          <button @click="showRelated = false" class="text-gray-400 hover:text-white">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
        
        <div class="space-y-2">
          <div
            v-for="item in relatedMedia"
            :key="item.id"
            class="flex items-center space-x-3 p-2 rounded hover:bg-gray-800 cursor-pointer"
            @click="playMedia(item)"
          >
            <img
              :src="getPosterUrl(item.id)"
              :alt="item.title || item.filename"
              class="w-12 h-16 object-cover rounded"
              @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
            />
            <div class="flex-1 min-w-0">
              <p class="text-white text-sm font-medium truncate">
                {{ item.title || item.filename }}
              </p>
              <p class="text-gray-400 text-xs capitalize">{{ item.category }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add to Playlist Modal -->
    <div v-if="showAddToPlaylist" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium mb-4">Add to Playlist</h3>
        <!-- Playlist selection content here -->
        <div class="flex gap-2 justify-end mt-4">
          <button @click="showAddToPlaylist = false" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium mb-4">Player Settings</h3>
        
        <div class="space-y-4">
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="autoplay"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="ml-2">Autoplay next media</span>
          </label>
          
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="showRelated"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="ml-2">Show related media</span>
          </label>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Default Volume
            </label>
            <input
              type="range"
              min="0"
              max="100"
              v-model="defaultVolume"
              class="w-full"
            />
            <span class="text-sm text-gray-500">{{ defaultVolume }}%</span>
          </div>
        </div>
        
        <div class="flex gap-2 justify-end mt-6">
          <button @click="showSettings = false" class="btn-outline">Close</button>
          <button @click="saveSettings" class="btn-primary">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeftIcon,
  PlusIcon,
  ShareIcon,
  ArrowDownTrayIcon,
  CogIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  DocumentIcon,
  ArrowsPointingOutIcon
} from '@heroicons/vue/24/outline'
import VideoPlayer from '@/components/players/VideoPlayer.vue'
import AudioPlayer from '@/components/players/AudioPlayer.vue'
import { mediaApi } from '@/api/media'
import type { MediaFile } from '@/types/media'

const route = useRoute()
const router = useRouter()

// State
const media = ref<MediaFile | null>(null)
const relatedMedia = ref<MediaFile[]>([])
const isLoading = ref(true)
const error = ref('')
const showAddToPlaylist = ref(false)
const showSettings = ref(false)
const showRelated = ref(false)

// Settings
const autoplay = ref(true)
const defaultVolume = ref(80)

// Computed
const mediaId = computed(() => route.params.id as string)

const isVideoContent = computed(() => {
  if (!media.value) return false
  
  const category = media.value.category?.toLowerCase()
  const filename = media.value.filename?.toLowerCase() || ''
  
  return category === 'movies' || 
         category === 'tv_shows' || 
         category === 'kids' || 
         category === 'videos' ||
         /\.(mp4|avi|mkv|mov|wmv|flv|webm|m4v)$/i.test(filename)
})

const isAudioContent = computed(() => {
  if (!media.value) return false
  
  const category = media.value.category?.toLowerCase()
  const filename = media.value.filename?.toLowerCase() || ''
  
  return category === 'music' ||
         /\.(mp3|wav|flac|aac|ogg|wma|m4a)$/i.test(filename)
})

const isImageContent = computed(() => {
  if (!media.value) return false
  
  const category = media.value.category?.toLowerCase()
  const filename = media.value.filename?.toLowerCase() || ''
  
  return category === 'photos' ||
         /\.(jpg|jpeg|png|gif|bmp|webp|svg|tiff|ico)$/i.test(filename)
})

const mediaUrl = computed(() => {
  if (!media.value?.id) return ''
  
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${media.value.id}/stream?token=${token}`
})

// Methods
async function loadMedia() {
  try {
    isLoading.value = true
    error.value = ''
    
    // Load main media
    const response = await mediaApi.getMediaFile(mediaId.value)
    media.value = response
    
    // Load related media (same category)
    if (media.value.category) {
      try {
        const relatedResponse = await mediaApi.getMediaFiles({
          category: media.value.category as any,
          page: 1,
          page_size: 20
        })
        
        // Filter out current media and limit to 10 items
        relatedMedia.value = (relatedResponse.items || relatedResponse.media || [])
          .filter((item: MediaFile) => item.id !== media.value?.id)
          .slice(0, 10)
      } catch (relatedError) {
        console.warn('Failed to load related media:', relatedError)
        relatedMedia.value = []
      }
    }
    
  } catch (err) {
    console.error('Failed to load media:', err)
    error.value = 'Media not found or failed to load'
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.back()
}

function playMedia(item: MediaFile) {
  router.push(`/player/${item.id}`)
}

function onPlay() {
  console.log('Media started playing')
}

function onPause() {
  console.log('Media paused')
}

function onEnded() {
  console.log('Media ended')
  
  if (autoplay.value && relatedMedia.value.length > 0) {
    // Play next related media
    const nextMedia = relatedMedia.value[0]
    playMedia(nextMedia)
  }
}

function onPlayerError(errorMessage: string) {
  error.value = errorMessage
}

function onTrackChanged(newMedia: MediaFile) {
  media.value = newMedia
  router.replace(`/player/${newMedia.id}`)
}

function onImageError() {
  error.value = 'Failed to load image'
}

async function shareMedia() {
  if (!media.value) return
  
  const shareData = {
    title: media.value.title || media.value.filename,
    text: `Check out this ${media.value.category}: ${media.value.title || media.value.filename}`,
    url: window.location.href
  }
  
  try {
    if (navigator.share) {
      await navigator.share(shareData)
    } else {
      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(window.location.href)
      alert('Link copied to clipboard!')
    }
  } catch (err) {
    console.error('Failed to share:', err)
  }
}

function downloadMedia() {
  if (!media.value?.id) return
  
  const downloadUrl = mediaUrl.value
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = media.value.filename || 'media-file'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

function saveSettings() {
  localStorage.setItem('watch1-player-settings', JSON.stringify({
    autoplay: autoplay.value,
    showRelated: showRelated.value,
    defaultVolume: defaultVolume.value
  }))
  
  showSettings.value = false
}

function loadSettings() {
  const saved = localStorage.getItem('watch1-player-settings')
  if (saved) {
    try {
      const settings = JSON.parse(saved)
      autoplay.value = settings.autoplay ?? true
      showRelated.value = settings.showRelated ?? false
      defaultVolume.value = settings.defaultVolume ?? 80
    } catch (error) {
      console.error('Failed to load player settings:', error)
    }
  }
}

function getPosterUrl(mediaId: string): string {
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  return `${cleanBaseUrl}/api/v1/media/${mediaId}/poster?token=${token}`
}

// Keyboard shortcuts
function handleKeyPress(event: KeyboardEvent) {
  switch (event.code) {
    case 'Space':
      event.preventDefault()
      // Toggle play/pause (handled by player components)
      break
    case 'Escape':
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        goBack()
      }
      break
    case 'KeyR':
      showRelated.value = !showRelated.value
      break
  }
}

// Lifecycle
onMounted(() => {
  loadSettings()
  loadMedia()
  document.addEventListener('keydown', handleKeyPress)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeyPress)
})

// Route changes handled in onMounted
</script>

<style scoped>
.control-btn {
  @apply bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all;
}

.btn-primary {
  @apply bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors;
}

.image-viewer {
  @apply relative min-h-screen bg-black;
}

.document-viewer {
  @apply relative min-h-screen bg-gray-900;
}
</style>
