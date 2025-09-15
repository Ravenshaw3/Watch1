<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Hero Section -->
    <div class="relative bg-gradient-to-r from-primary-600 to-primary-800">
      <div class="absolute inset-0 bg-black opacity-20"></div>
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div class="text-center">
          <h1 class="text-4xl md:text-6xl font-bold text-white mb-6">
            Welcome to Watch1
          </h1>
          <p class="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
            High-performance media server with advanced features for managing your media library
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link
              v-if="!authStore.isAuthenticated"
              to="/register"
              class="btn bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 text-lg font-medium"
            >
              Get Started
            </router-link>
            <router-link
              v-else
              to="/library"
              class="btn bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 text-lg font-medium"
            >
              View Library
            </router-link>
            <router-link
              to="/library"
              class="btn border-2 border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3 text-lg font-medium"
            >
              Browse Media
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="py-16 bg-white dark:bg-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Powerful Features
          </h2>
          <p class="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Everything you need to manage and enjoy your media collection
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="text-center">
            <div class="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <FilmIcon class="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Media Management
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              Organize and manage your media files with drag & drop, batch operations, and smart collections.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="text-center">
            <div class="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <PlayIcon class="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Advanced Player
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              Picture-in-picture mode, multiple subtitle tracks, and advanced video controls.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="text-center">
            <div class="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <CpuChipIcon class="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Smart Features
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              AI-powered recommendations, automatic genre detection, and smart search with filters.
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="text-center">
            <div class="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <CloudIcon class="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              High Performance
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              Optimized for large libraries with 10,000+ files and real-time streaming.
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="text-center">
            <div class="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <ListBulletIcon class="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Smart Playlists
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              Create dynamic playlists with filters and automatic content-based recommendations.
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="text-center">
            <div class="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShieldCheckIcon class="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Secure & Private
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              Your media stays private with secure authentication and encrypted connections.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Media Section -->
    <div v-if="authStore.isAuthenticated && recentMedia.length > 0" class="py-16 bg-gray-50 dark:bg-gray-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
            Recent Media
          </h2>
          <router-link
            to="/library"
            class="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
          >
            View All →
          </router-link>
        </div>

        <div class="media-grid">
          <MediaCard
            v-for="media in recentMedia"
            :key="media.id"
            :media="media"
            @click="viewMedia(media)"
          />
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div v-if="!authStore.isAuthenticated" class="py-16 bg-primary-600">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl font-bold text-white mb-4">
          Ready to get started?
        </h2>
        <p class="text-xl text-primary-100 mb-8">
          Create your account and start managing your media library today.
        </p>
        <router-link
          to="/register"
          class="btn bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 text-lg font-medium"
        >
          Create Account
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMediaStore } from '@/stores/media'
import MediaCard from '@/components/media/MediaCard.vue'
import {
  FilmIcon,
  PlayIcon,
  CpuChipIcon,
  CloudIcon,
  ListBulletIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const mediaStore = useMediaStore()

const recentMedia = computed(() => mediaStore.recentFiles.slice(0, 12))

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await mediaStore.fetchMediaFiles()
  }
})

function viewMedia(media: any) {
  router.push({
    name: 'MediaDetail',
    params: { id: media.id }
  })
}
</script>
