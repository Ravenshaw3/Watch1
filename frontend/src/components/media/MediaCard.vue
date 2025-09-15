<template>
  <div
    class="media-card cursor-pointer"
    @click="$emit('click', media)"
  >
    <!-- Poster/Thumbnail -->
    <div class="relative">
        <img
          v-if="isImage"
          :src="mediaUrl"
          :alt="media.original_filename"
          class="media-poster"
          loading="lazy"
        />
        <div
          v-else
          class="media-poster bg-gray-700 flex items-center justify-center"
        >
          <component
            :is="mediaIcon"
            class="h-12 w-12 text-gray-400"
          />
        </div>

      <!-- Overlay -->
      <div class="media-overlay">
        <div class="media-info">
          <h3 class="media-title">
            {{ media.original_filename }}
          </h3>
          <div class="media-meta">
            <span v-if="media.duration">
              {{ formatDuration(media.duration) }}
            </span>
            <span class="ml-2">
              {{ formatFileSize(media.file_size) }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="absolute top-4 right-4 flex space-x-2">
          <button
            v-if="isVideo"
            @click.stop="playMedia"
            class="bg-black bg-opacity-50 hover:bg-opacity-70 text-white p-2 rounded-full transition-all duration-200"
            title="Play"
          >
            <PlayIcon class="h-4 w-4" />
          </button>
          <button
            @click.stop="showMenu = !showMenu"
            class="bg-black bg-opacity-50 hover:bg-opacity-70 text-white p-2 rounded-full transition-all duration-200"
            title="More options"
          >
            <EllipsisVerticalIcon class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div
      v-show="showMenu"
      class="absolute top-12 right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg py-2 z-10 min-w-[160px]"
      @click.stop
    >
      <button
        @click="playMedia"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        <PlayIcon class="h-4 w-4 inline mr-2" />
        Play
      </button>
      <button
        @click="viewDetails"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        <EyeIcon class="h-4 w-4 inline mr-2" />
        View Details
      </button>
      <button
        @click="addToPlaylist"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        <PlusIcon class="h-4 w-4 inline mr-2" />
        Add to Playlist
      </button>
      <hr class="my-2 border-gray-200 dark:border-gray-600" />
      <button
        @click="downloadMedia"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        <ArrowDownTrayIcon class="h-4 w-4 inline mr-2" />
        Download
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { MediaFile } from '@/types/media'
import {
  PlayIcon,
  EllipsisVerticalIcon,
  EyeIcon,
  PlusIcon,
  ArrowDownTrayIcon,
  FilmIcon,
  MusicalNoteIcon,
  PhotoIcon
} from '@heroicons/vue/24/outline'

interface Props {
  media: MediaFile
}

const props = defineProps<Props>()
const emit = defineEmits<{
  click: [media: MediaFile]
}>()

const router = useRouter()
const showMenu = ref(false)

const mediaUrl = computed(() => {
  return `http://192.168.254.14:8000/media/${props.media.filename}`
})

const isVideo = computed(() => {
  return props.media.mime_type.startsWith('video/')
})

const isImage = computed(() => {
  return props.media.mime_type.startsWith('image/')
})

const isAudio = computed(() => {
  return props.media.mime_type.startsWith('audio/')
})

const mediaIcon = computed(() => {
  if (isVideo.value) return FilmIcon
  if (isAudio.value) return MusicalNoteIcon
  if (isImage.value) return PhotoIcon
  return FilmIcon
})

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

function playMedia() {
  if (isVideo.value) {
    // For now, just open the media URL directly
    window.open(mediaUrl.value, '_blank')
  }
  showMenu.value = false
}

function viewDetails() {
  // For now, just show an alert with media info
  alert(`Media Details:\nFilename: ${props.media.original_filename}\nSize: ${formatFileSize(props.media.file_size)}\nType: ${props.media.mime_type}`)
  showMenu.value = false
}

function addToPlaylist() {
  // TODO: Implement add to playlist functionality
  showMenu.value = false
}

function downloadMedia() {
  // Download the media file
  const link = document.createElement('a')
  link.href = mediaUrl.value
  link.download = props.media.original_filename
  link.click()
  showMenu.value = false
}
</script>
