<template>
  <div class="fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg text-sm max-w-sm">
    <h3 class="font-bold mb-2">Navigation Debug</h3>
    <div class="space-y-1">
      <div>Current Route: {{ currentRoute }}</div>
      <div>Auth Status: {{ authStatus }}</div>
      <div>Token Present: {{ tokenPresent }}</div>
      <div>User Loaded: {{ userLoaded }}</div>
      <div>Last Error: {{ lastError }}</div>
    </div>
    <div class="mt-2 space-x-2">
      <button @click="testNavigation" class="bg-blue-500 px-2 py-1 rounded text-xs">
        Test Nav
      </button>
      <button @click="clearError" class="bg-red-500 px-2 py-1 rounded text-xs">
        Clear
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const lastError = ref('')

const currentRoute = computed(() => route.path)
const authStatus = computed(() => authStore.isAuthenticated ? 'Authenticated' : 'Not Authenticated')
const tokenPresent = computed(() => authStore.token ? 'Yes' : 'No')
const userLoaded = computed(() => authStore.user ? 'Yes' : 'No')

// Route and auth changes logged via computed properties

// Capture navigation errors
router.onError((error) => {
  console.error('Router error:', error)
  lastError.value = error.message
})

async function testNavigation() {
  const routes = ['/library', '/playlists', '/analytics', '/settings']
  
  for (const route of routes) {
    try {
      console.log(`Testing navigation to ${route}`)
      await router.push(route)
      await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1 second
    } catch (error) {
      console.error(`Navigation to ${route} failed:`, error)
      lastError.value = `Failed to navigate to ${route}: ${error}`
      break
    }
  }
}

function clearError() {
  lastError.value = ''
}
</script>
