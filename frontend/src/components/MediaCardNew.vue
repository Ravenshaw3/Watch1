<template>
  <div class="media-card" @click="handleClick">
    <div class="media-poster">
      <img
        v-if="posterUrl && !imageError"
        :src="posterUrl"
        :alt="displayTitle"
        class="poster-image"
        @error="onImageError"
        @load="onImageLoad"
      />
      <div v-if="!posterUrl || imageError" class="poster-placeholder">
        <FilmIcon class="w-16 h-16 text-gray-400" />
      </div>
      
      <!-- Play overlay with media type icon -->
      <div class="play-overlay">
        <PlayIcon v-if="isVideoMedia" class="w-12 h-12 text-white" />
        <MusicalNoteIcon v-else-if="isAudioMedia" class="w-12 h-12 text-white" />
        <PhotoIcon v-else-if="isImageMedia" class="w-12 h-12 text-white" />
        <DocumentIcon v-else class="w-12 h-12 text-white" />
      </div>
      
      <!-- Add to Playlist button -->
      <div class="playlist-button">
        <button 
          @click.stop="openAddToPlaylistModal"
          class="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all"
          title="Add to Playlist"
        >
          <PlusIcon class="w-5 h-5" />
        </button>
      </div>
      
      <!-- Duration badge -->
      <div v-if="safeMedia?.duration" class="duration-badge">
        {{ formatDuration(safeMedia.duration) }}
      </div>
    </div>
    
    <div class="media-info">
      <h3 class="media-title">{{ displayTitle }}</h3>
      <div class="media-meta">
        <span class="category">{{ displayCategory }}</span>
        <span class="file-size">{{ displayFileSize }}</span>
      </div>
    </div>
  </div>
  
  <!-- Add to Playlist Modal -->
  <div v-if="showAddToPlaylist" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="showAddToPlaylist = false">
    <div class="bg-white rounded-lg p-6 w-full max-w-md" @click.stop>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium">Add to Playlist</h3>
        <button @click="showAddToPlaylist = false" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-6 w-6" />
        </button>
      </div>
      
      <div v-if="isLoadingPlaylists" class="text-center py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-2 text-gray-600">Loading playlists...</p>
      </div>
      
      <div v-else-if="playlists.length === 0" class="text-center py-4">
        <p class="text-gray-600">No playlists available</p>
      </div>
      
      <div v-else class="space-y-2 max-h-60 overflow-y-auto">
        <button
          v-for="playlist in playlists"
          :key="playlist.id"
          @click="addToPlaylist(playlist.id)"
          class="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div class="font-medium">{{ playlist.name }}</div>
          <div v-if="playlist.description" class="text-sm text-gray-600">{{ playlist.description }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ playlist.items?.length || 0 }} items</div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { FilmIcon, PlayIcon, PlusIcon, XMarkIcon, MusicalNoteIcon, PhotoIcon, DocumentIcon } from '@heroicons/vue/24/outline'
import { mediaApi } from '@/api/media'
import type { MediaFile, Playlist } from '@/types/media'

interface Props {
  media?: MediaFile | null
}

const props = defineProps<Props>()
const router = useRouter()

// Reactive state
const showAddToPlaylist = ref(false)
const playlists = ref<Playlist[]>([])
const isLoadingPlaylists = ref(false)
const imageError = ref(false)

// Safe media object with null checks
const safeMedia = computed(() => {
  if (!props.media || typeof props.media !== 'object') {
    return null
  }
  return props.media
})

// Safe computed properties with fallbacks
const displayTitle = computed(() => {
  if (!safeMedia.value) return 'Unknown Media'
  
  // Priority: title > cleaned filename > original_filename > fallback
  let title = safeMedia.value.title
  
  if (!title) {
    // Use filename and clean it up
    const rawTitle = safeMedia.value.filename || safeMedia.value.original_filename
    if (rawTitle) {
      // Remove file extension and clean up common patterns
      title = rawTitle
        .replace(/\.[^/.]+$/, '') // Remove file extension
        .replace(/[\._]/g, ' ')   // Replace dots and underscores with spaces
        .replace(/\s+/g, ' ')     // Collapse multiple spaces
        .trim()
    }
  }
  
  return title || 'Unknown Media'
})

const displayCategory = computed(() => {
  const category = safeMedia.value?.category
  if (!category || category === 'other') return 'Media'
  return category.charAt(0).toUpperCase() + category.slice(1)
})

const displayFileSize = computed(() => {
  const size = safeMedia.value?.file_size
  if (!size || typeof size !== 'number') return ''
  return formatFileSize(size)
})

const posterUrl = computed(() => {
  if (!safeMedia.value?.id) return ''
  
  // Use the dedicated poster endpoint with auth token
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'
  const cleanBaseUrl = baseUrl.replace('/api/v1', '')
  const token = localStorage.getItem('access_token')
  
  // Include token in URL for image requests (since img tags can't send headers)
  return `${cleanBaseUrl}/api/v1/media/${safeMedia.value.id}/poster?token=${token}`
})

// Media type detection
const isVideoMedia = computed(() => {
  const category = safeMedia.value?.category?.toLowerCase()
  const filename = safeMedia.value?.filename?.toLowerCase() || ''
  
  return category === 'movies' || 
         category === 'tv_shows' || 
         category === 'kids' || 
         category === 'videos' ||
         /\.(mp4|avi|mkv|mov|wmv|flv|webm|m4v)$/i.test(filename)
})

const isAudioMedia = computed(() => {
  const category = safeMedia.value?.category?.toLowerCase()
  const filename = safeMedia.value?.filename?.toLowerCase() || ''
  
  return category === 'music' ||
         /\.(mp3|wav|flac|aac|ogg|wma|m4a)$/i.test(filename)
})

const isImageMedia = computed(() => {
  const category = safeMedia.value?.category?.toLowerCase()
  const filename = safeMedia.value?.filename?.toLowerCase() || ''
  
  return category === 'photos' ||
         /\.(jpg|jpeg|png|gif|bmp|webp|svg|tiff|ico)$/i.test(filename)
})

// Utility functions
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDuration(seconds: number): string {
  if (!seconds || typeof seconds !== 'number') return ''
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}


function handleClick(event: Event) {
  console.log('=== MediaCard Click Handler ===')
  console.log('Event:', event)
  console.log('MediaCard clicked:', safeMedia.value)
  console.log('Media ID:', safeMedia.value?.id)
  
  // Prevent any default behavior
  event.preventDefault()
  event.stopPropagation()
  
  if (!safeMedia.value?.id) {
    console.warn('MediaCard: No media ID available for navigation')
    console.warn('Media object:', safeMedia.value)
    return
  }
  
  const targetRoute = `/player/${safeMedia.value.id}`
  console.log('Navigating to:', targetRoute)
  console.log('Router object:', router)
  
  try {
    const result = router.push(targetRoute)
    console.log('Navigation result:', result)
    console.log('Navigation successful')
  } catch (error) {
    console.error('MediaCard: Navigation error:', error)
  }
}

// Playlist functions
async function loadPlaylists() {
  if (isLoadingPlaylists.value) return
  
  isLoadingPlaylists.value = true
  try {
    const response = await mediaApi.getPlaylists()
    // Handle the response structure properly
    if (response && (response as any).playlists && Array.isArray((response as any).playlists)) {
      playlists.value = (response as any).playlists
    } else if (Array.isArray(response)) {
      playlists.value = response
    } else {
      console.warn('Unexpected playlists response:', response)
      playlists.value = []
    }
    console.log('Loaded playlists:', playlists.value)
  } catch (error) {
    console.error('Failed to load playlists:', error)
    playlists.value = []
  } finally {
    isLoadingPlaylists.value = false
  }
}

async function addToPlaylist(playlistId: string) {
  if (!safeMedia.value?.id) {
    console.error('No media ID available')
    return
  }
  
  try {
    await mediaApi.addPlaylistItem(playlistId, {
      media_id: safeMedia.value.id
    })
    
    showAddToPlaylist.value = false
    console.log('Successfully added to playlist')
    
    // Optional: Show success message
    // You could emit an event here or use a toast notification
  } catch (error) {
    console.error('Failed to add to playlist:', error)
    // Optional: Show error message
  }
}

// Watch for modal opening to load playlists
function openAddToPlaylistModal() {
  showAddToPlaylist.value = true
  loadPlaylists()
}

function onImageError() {
  console.warn('MediaCard: Image failed to load:', posterUrl.value)
  imageError.value = true
}

function onImageLoad() {
  console.log('MediaCard: Image loaded successfully:', posterUrl.value)
  imageError.value = false
}

// Image error reset handled in onImageLoad/onImageError
</script>

<style scoped>
.media-card {
  @apply bg-white rounded-lg shadow-md overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105;
}

.media-poster {
  @apply relative aspect-[2/3] bg-gray-100;
}

.poster-image {
  @apply w-full h-full object-cover;
}

.poster-placeholder {
  @apply w-full h-full flex items-center justify-center bg-gray-200;
}

.play-overlay {
  @apply absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 transition-opacity duration-200;
}

.playlist-button {
  @apply absolute top-2 right-2 opacity-0 transition-opacity duration-200;
}

.media-card:hover .play-overlay,
.media-card:hover .playlist-button {
  @apply opacity-100;
}

.duration-badge {
  @apply absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded;
}

.media-info {
  @apply p-4;
}

.media-title {
  @apply font-semibold text-gray-900 truncate mb-2;
}

.media-meta {
  @apply flex justify-between items-center text-sm text-gray-500;
}

.category {
  @apply capitalize;
}
</style>
