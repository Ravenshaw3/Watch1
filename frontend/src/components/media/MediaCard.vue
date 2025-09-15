<template>
  <div
    class="media-card cursor-pointer"
    @click="$emit('click', media)"
  >
    <!-- Poster/Thumbnail -->
    <div class="relative">
      <img
        v-if="posterUrl"
        :src="posterUrl"
        :alt="media.metadata?.title || media.filename"
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
            {{ media.metadata?.title || media.filename }}
          </h3>
          <div class="media-meta">
            <span v-if="media.metadata?.year">{{ media.metadata.year }}</span>
            <span v-if="media.metadata?.genre" class="ml-2">
              {{ media.metadata.genre }}
            </span>
            <span v-if="media.duration" class="ml-2">
              {{ formatDuration(media.duration) }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="absolute top-4 right-4 flex space-x-2">
          <button
            v-if="media.media_type === 'video'"
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

const posterUrl = computed(() => {
  if (props.media.poster_path) {
    return `/api/v1/media/${props.media.id}/poster`
  }
  if (props.media.thumbnail_path) {
    return `/api/v1/media/${props.media.id}/thumbnail`
  }
  return null
})

const mediaIcon = computed(() => {
  switch (props.media.media_type) {
    case 'video':
      return FilmIcon
    case 'audio':
      return MusicalNoteIcon
    case 'image':
      return PhotoIcon
    default:
      return FilmIcon
  }
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

function playMedia() {
  if (props.media.media_type === 'video') {
    router.push({
      name: 'Player',
      params: { id: props.media.id }
    })
  }
  showMenu.value = false
}

function viewDetails() {
  router.push({
    name: 'MediaDetail',
    params: { id: props.media.id }
  })
  showMenu.value = false
}

function addToPlaylist() {
  // TODO: Implement add to playlist functionality
  showMenu.value = false
}

function downloadMedia() {
  // TODO: Implement download functionality
  showMenu.value = false
}
</script>
