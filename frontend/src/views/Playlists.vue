<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Playlists
            </h1>
            <p class="mt-2 text-gray-600">
              Create and manage your media playlists
            </p>
          </div>
          <button
            @click="showCreateModal = true"
            class="btn-primary"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            Create Playlist
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading playlists...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="playlists.length === 0" class="text-center py-12">
        <MusicalNoteIcon class="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          No playlists found
        </h3>
        <p class="text-gray-600 mb-6">
          Create your first playlist to organize your media.
        </p>
        <button @click="showCreateModal = true" class="btn-primary">
          Create Playlist
        </button>
      </div>

      <!-- Playlists Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="playlist in playlists"
          :key="playlist.id"
          class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
        >
          <!-- Playlist Header -->
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="font-semibold text-lg text-gray-900">
                  {{ playlist.name }}
                </h3>
                <p v-if="playlist.description" class="text-sm text-gray-600 mt-1">
                  {{ playlist.description }}
                </p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editPlaylist(playlist)"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <PencilIcon class="h-4 w-4" />
                </button>
                <button
                  @click="deletePlaylist(playlist.id)"
                  class="text-gray-400 hover:text-red-600"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between text-sm text-gray-500">
              <span>{{ playlist.items.length }} items</span>
              <span>{{ formatDate(playlist.updated_at) }}</span>
            </div>
          </div>

          <!-- Playlist Actions -->
          <div class="px-6 pb-6">
            <div class="flex space-x-2">
              <button
                @click="viewPlaylist(playlist)"
                class="flex-1 btn-outline"
              >
                <EyeIcon class="h-4 w-4 mr-2" />
                View
              </button>
              <button
                @click="playPlaylist(playlist)"
                class="flex-1 btn-primary"
              >
                <PlayIcon class="h-4 w-4 mr-2" />
                Play
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Playlist Modal -->
      <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 class="text-lg font-medium mb-4">Create New Playlist</h3>
          
          <form @submit.prevent="createPlaylist">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  v-model="newPlaylist.name"
                  type="text"
                  required
                  class="input"
                  placeholder="Enter playlist name"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  v-model="newPlaylist.description"
                  class="input"
                  rows="3"
                  placeholder="Enter playlist description (optional)"
                />
              </div>
              
              <div class="flex items-center">
                <input
                  v-model="newPlaylist.is_public"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label class="ml-2 block text-sm text-gray-900">
                  Make playlist public
                </label>
              </div>
            </div>
            
            <div class="flex gap-2 justify-end mt-6">
              <button
                type="button"
                @click="showCreateModal = false"
                class="btn-outline"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isCreating"
                class="btn-primary"
              >
                <span v-if="isCreating">Creating...</span>
                <span v-else>Create</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Playlist Detail Modal -->
      <div v-if="selectedPlaylist" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ selectedPlaylist.name }}
            </h2>
            <button @click="selectedPlaylist = null" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>

          <p v-if="selectedPlaylist.description" class="text-gray-600 mb-6">
            {{ selectedPlaylist.description }}
          </p>

          <!-- Playlist Items -->
          <div v-if="playlistMedia.length > 0" class="space-y-4">
            <div
              v-for="(media, index) in playlistMedia"
              :key="media.id"
              class="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg"
            >
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span class="text-white font-semibold text-sm">
                    {{ index + 1 }}
                  </span>
                </div>
              </div>
              
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ media.original_filename }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ getCategoryDisplayName(media.category) }} • {{ formatFileSize(media.file_size) }}
                </p>
              </div>
              
              <div class="flex space-x-2">
                <button
                  @click="playMedia(media)"
                  class="text-gray-400 hover:text-primary-600"
                >
                  <PlayIcon class="h-5 w-5" />
                </button>
                <button
                  @click="removeFromPlaylist(media.id)"
                  class="text-gray-400 hover:text-red-600"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <MusicalNoteIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-600">This playlist is empty</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mediaApi } from '@/api/media'
import type { Playlist, PlaylistCreate, MediaFile } from '@/types/media'
import { 
  PlusIcon, 
  MusicalNoteIcon, 
  PlayIcon, 
  EyeIcon, 
  PencilIcon, 
  TrashIcon, 
  XMarkIcon 
} from '@heroicons/vue/24/outline'

const playlists = ref<Playlist[]>([])
const selectedPlaylist = ref<Playlist | null>(null)
const playlistMedia = ref<MediaFile[]>([])
const isLoading = ref(false)
const isCreating = ref(false)
const showCreateModal = ref(false)

const newPlaylist = ref<PlaylistCreate>({
  name: '',
  description: '',
  is_public: false
})

async function loadPlaylists() {
  isLoading.value = true
  try {
    playlists.value = await mediaApi.getPlaylists()
  } catch (error) {
    console.error('Failed to load playlists:', error)
  } finally {
    isLoading.value = false
  }
}

async function createPlaylist() {
  isCreating.value = true
  try {
    await mediaApi.createPlaylist(newPlaylist.value)
    showCreateModal.value = false
    newPlaylist.value = { name: '', description: '', is_public: false }
    await loadPlaylists()
  } catch (error) {
    console.error('Failed to create playlist:', error)
  } finally {
    isCreating.value = false
  }
}

async function deletePlaylist(playlistId: string) {
  if (!confirm('Are you sure you want to delete this playlist?')) return
  
  try {
    await mediaApi.deletePlaylist(playlistId)
    await loadPlaylists()
  } catch (error) {
    console.error('Failed to delete playlist:', error)
  }
}

async function viewPlaylist(playlist: Playlist) {
  selectedPlaylist.value = playlist
  try {
    const response = await mediaApi.getPlaylistMedia(playlist.id)
    playlistMedia.value = response.media
  } catch (error) {
    console.error('Failed to load playlist media:', error)
  }
}

async function playPlaylist(playlist: Playlist) {
  try {
    const response = await mediaApi.getPlaylistMedia(playlist.id)
    if (response.media.length > 0) {
      await playMedia(response.media[0])
    }
  } catch (error) {
    console.error('Failed to play playlist:', error)
  }
}

async function playMedia(media: MediaFile) {
  try {
    const streamUrl = await mediaApi.streamMediaFile(media.id)
        const fullUrl = `http://localhost:8000${streamUrl}`
    window.open(fullUrl, '_blank')
  } catch (error) {
    console.error('Failed to play media:', error)
  }
}

async function removeFromPlaylist(mediaId: string) {
  if (!selectedPlaylist.value) return
  
  try {
    await mediaApi.removePlaylistItem(selectedPlaylist.value.id, mediaId)
    await viewPlaylist(selectedPlaylist.value) // Refresh the view
  } catch (error) {
    console.error('Failed to remove from playlist:', error)
  }
}

function editPlaylist(playlist: Playlist) {
  // TODO: Implement edit functionality
  console.log('Edit playlist:', playlist)
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
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
    'tv_shows': 'TV Show',
    'kids': 'Kids',
    'music_videos': 'Music Video',
    'audio': 'Audio',
    'images': 'Image',
    'other': 'Other'
  }
  return categoryMap[category] || category
}

onMounted(() => {
  loadPlaylists()
})
</script>
