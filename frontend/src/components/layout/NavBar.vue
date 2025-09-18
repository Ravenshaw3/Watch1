<template>
  <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo and Navigation -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-2xl font-bold text-primary-600">Watch1</h1>
            </div>
          </router-link>
          
                  <!-- Desktop Navigation -->
                  <div class="hidden md:ml-6 md:flex md:space-x-8">
                    <router-link
                      to="/library"
                      class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      active-class="text-primary-600 dark:text-primary-400"
                    >
                      Library
                    </router-link>
                    <router-link
                      to="/tv-series"
                      class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      active-class="text-primary-600 dark:text-primary-400"
                    >
                      TV Series
                    </router-link>
                    <router-link
                      to="/playlists"
                      class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      active-class="text-primary-600 dark:text-primary-400"
                    >
                      Playlists
                    </router-link>
                    <router-link
                      to="/analytics"
                      class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      active-class="text-primary-600 dark:text-primary-400"
                    >
                      Analytics
                    </router-link>
                  </div>
        </div>

        <!-- Search Bar -->
        <div class="flex-1 flex items-center justify-center px-2 lg:ml-6 lg:justify-end">
          <div class="max-w-lg w-full lg:max-w-xs">
            <label for="search" class="sr-only">Search</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="search"
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm text-gray-900 dark:text-white"
                placeholder="Search media..."
                type="search"
              />
            </div>
          </div>
        </div>

        <!-- User Menu -->
        <div class="flex items-center">
          <!-- Version Info -->
          <VersionInfo class="mr-4" />
          
          <div v-if="authStore.isAuthenticated" class="ml-4 flex items-center md:ml-6">
            <!-- Upload Button -->
            <router-link
              to="/upload"
              class="btn-outline mr-4"
            >
              <PlusIcon class="h-4 w-4 mr-2" />
              Upload
            </router-link>

            <!-- User Dropdown -->
            <div class="ml-3 relative">
              <div>
                <button
                  @click="showUserMenu = !showUserMenu"
                  class="max-w-xs bg-white dark:bg-gray-800 flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  <span class="sr-only">Open user menu</span>
                  <div class="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center">
                    <span class="text-sm font-medium text-white">
                      {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                </button>
              </div>

              <!-- Dropdown Menu -->
              <div
                v-show="showUserMenu"
                class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
              >
                <router-link
                  to="/profile"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="showUserMenu = false"
                >
                  Your Profile
                </router-link>
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>

          <!-- Login/Register Links -->
          <div v-else class="flex items-center space-x-4">
            <router-link
              to="/login"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              class="btn-primary"
            >
              Register
            </router-link>
          </div>
        </div>
      </div>
    </div>

            <!-- Mobile menu -->
            <div v-show="showMobileMenu" class="md:hidden">
              <div class="pt-2 pb-3 space-y-1">
                <router-link
                  to="/library"
                  class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                  @click="showMobileMenu = false"
                >
                  Library
                </router-link>
                <router-link
                  to="/tv-series"
                  class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                  @click="showMobileMenu = false"
                >
                  TV Series
                </router-link>
                <router-link
                  to="/playlists"
                  class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                  @click="showMobileMenu = false"
                >
                  Playlists
                </router-link>
                <router-link
                  to="/analytics"
                  class="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                  @click="showMobileMenu = false"
                >
                  Analytics
                </router-link>
              </div>
            </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { MagnifyingGlassIcon, PlusIcon } from '@heroicons/vue/24/outline'
import VersionInfo from '@/components/VersionInfo.vue'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const showUserMenu = ref(false)
const showMobileMenu = ref(false)

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'Search',
      query: { q: searchQuery.value }
    })
    searchQuery.value = ''
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/')
  showUserMenu.value = false
}
</script>
