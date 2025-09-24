<template>
  <div class="debug-page">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8">🔍 Debug Information</h1>
      
      <!-- API Status -->
      <div class="debug-section">
        <h2 class="text-xl font-semibold mb-4">API Status</h2>
        <div class="debug-card">
          <button @click="testAPI" class="btn-primary mb-4">Test API Connection</button>
          <pre v-if="apiStatus" class="debug-output">{{ apiStatus }}</pre>
        </div>
      </div>

      <!-- Media List -->
      <div class="debug-section">
        <h2 class="text-xl font-semibold mb-4">Media Files</h2>
        <div class="debug-card">
          <button @click="loadMediaList" class="btn-primary mb-4">Load Media List</button>
          <div v-if="mediaList">
            <p class="mb-2">Total: {{ mediaList.total }} files</p>
            <div v-if="mediaList.media && mediaList.media.length > 0">
              <h3 class="font-semibold mb-2">First 5 Media Files:</h3>
              <div v-for="media in mediaList.media.slice(0, 5)" :key="media.id" class="media-debug-item">
                <div class="flex justify-between items-center p-2 border rounded">
                  <div>
                    <strong>ID:</strong> {{ media.id }} | 
                    <strong>File:</strong> {{ media.original_filename }}
                  </div>
                  <button @click="testMediaFile(media.id)" class="btn-sm">Test</button>
                </div>
              </div>
            </div>
            <pre v-else class="debug-output">{{ JSON.stringify(mediaList, null, 2) }}</pre>
          </div>
        </div>
      </div>

      <!-- Media File Test -->
      <div class="debug-section">
        <h2 class="text-xl font-semibold mb-4">Individual Media File Test</h2>
        <div class="debug-card">
          <div class="flex gap-2 mb-4">
            <input 
              v-model="testMediaId" 
              placeholder="Enter media ID" 
              class="border px-3 py-2 rounded"
            />
            <button @click="testMediaFile(testMediaId)" class="btn-primary">Test Media File</button>
          </div>
          <pre v-if="mediaFileResult" class="debug-output">{{ mediaFileResult }}</pre>
        </div>
      </div>

      <!-- Navigation Test -->
      <div class="debug-section">
        <h2 class="text-xl font-semibold mb-4">Navigation Test</h2>
        <div class="debug-card">
          <div class="flex gap-2 mb-4">
            <input 
              v-model="navTestId" 
              placeholder="Enter media ID for navigation" 
              class="border px-3 py-2 rounded"
            />
            <button @click="testNavigation" class="btn-primary">Test Navigation</button>
          </div>
          <p class="text-sm text-gray-600">This will navigate to the MediaPlayer page</p>
        </div>
      </div>

      <!-- Console Logs -->
      <div class="debug-section">
        <h2 class="text-xl font-semibold mb-4">Console Logs</h2>
        <div class="debug-card">
          <button @click="clearLogs" class="btn-outline mb-4">Clear Console</button>
          <p class="text-sm text-gray-600">
            Check the browser console (F12) for detailed debug information.
            All API calls and navigation attempts are logged there.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { mediaApi } from '@/api/media'

const router = useRouter()

// State
const apiStatus = ref('')
const mediaList = ref<any>(null)
const mediaFileResult = ref('')
const testMediaId = ref('')
const navTestId = ref('')

// Methods
const testAPI = async () => {
  try {
    apiStatus.value = 'Testing API connection...'
    
    // Test basic API connectivity
    const response = await fetch('http://localhost:8000/api/v1/health')
    if (response.ok) {
      apiStatus.value = '✅ API connection successful\n'
    } else {
      apiStatus.value = `❌ API connection failed: ${response.status}\n`
    }
    
    // Test authentication
    const token = localStorage.getItem('access_token')
    if (token) {
      apiStatus.value += '✅ Access token found\n'
      
      // Test authenticated endpoint
      const authResponse = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (authResponse.ok) {
        apiStatus.value += '✅ Authentication working\n'
      } else {
        apiStatus.value += `❌ Authentication failed: ${authResponse.status}\n`
      }
    } else {
      apiStatus.value += '❌ No access token found\n'
    }
    
  } catch (error) {
    apiStatus.value = `❌ API test failed: ${error}`
  }
}

const loadMediaList = async () => {
  try {
    console.log('🔍 Debug: Loading media list...')
    mediaList.value = await mediaApi.getMediaFiles({ page: 1, page_size: 10 })
    console.log('🔍 Debug: Media list loaded:', mediaList.value)
  } catch (error) {
    console.error('🔍 Debug: Failed to load media list:', error)
    mediaList.value = { error: String(error) }
  }
}

const testMediaFile = async (id: string | number) => {
  if (!id) {
    mediaFileResult.value = 'Please enter a media ID'
    return
  }
  
  try {
    console.log(`🔍 Debug: Testing media file ID: ${id}`)
    const result = await mediaApi.getMediaFile(id)
    console.log('🔍 Debug: Media file result:', result)
    mediaFileResult.value = JSON.stringify(result, null, 2)
  } catch (error) {
    console.error('🔍 Debug: Failed to get media file:', error)
    mediaFileResult.value = `Error: ${error}`
  }
}

const testNavigation = () => {
  if (!navTestId.value) {
    alert('Please enter a media ID')
    return
  }
  
  console.log(`🔍 Debug: Navigating to /player/${navTestId.value}`)
  router.push(`/player/${navTestId.value}`)
}

const clearLogs = () => {
  console.clear()
  console.log('🔍 Debug: Console cleared')
}
</script>

<style scoped>
.debug-page {
  min-height: 100vh;
  background: #f9fafb;
}

.debug-section {
  margin-bottom: 2rem;
}

.debug-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.debug-output {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.media-debug-item {
  margin-bottom: 0.5rem;
}

.btn-primary {
  @apply bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 transition-colors;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 px-4 py-2 rounded font-medium hover:bg-gray-50 transition-colors;
}

.btn-sm {
  @apply bg-gray-100 text-gray-700 px-2 py-1 text-sm rounded hover:bg-gray-200 transition-colors;
}
</style>
