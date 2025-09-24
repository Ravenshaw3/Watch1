<template>
  <div class="media-scanner">
    <div class="scanner-header">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        📡 Media Scanner
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Scan media directories to discover new files and update poster artwork automatically.
      </p>
    </div>

    <div class="scanner-controls mb-6">
      <button
        @click="startScan"
        :disabled="isScanning"
        class="scan-button"
        :class="{
          'scanning': isScanning,
          'idle': !isScanning
        }"
      >
        <span v-if="!isScanning" class="flex items-center">
          🔍 <span class="ml-2">Start Media Scan</span>
        </span>
        <span v-else class="flex items-center">
          ⏳ <span class="ml-2">Scanning...</span>
        </span>
      </button>
    </div>

    <div v-if="scanResult" class="scan-results">
      <div class="results-header">
        <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
          📊 Scan Results
        </h4>
      </div>

      <div class="results-grid">
        <div class="result-card">
          <div class="result-icon">🆕</div>
          <div class="result-content">
            <div class="result-number">{{ scanResult.new_files || 0 }}</div>
            <div class="result-label">New Files</div>
          </div>
        </div>

        <div class="result-card">
          <div class="result-icon">🔄</div>
          <div class="result-content">
            <div class="result-number">{{ scanResult.updated_files || 0 }}</div>
            <div class="result-label">Updated Files</div>
          </div>
        </div>

        <div class="result-card">
          <div class="result-icon">🖼️</div>
          <div class="result-content">
            <div class="result-number">{{ scanResult.posters_loaded || 0 }}</div>
            <div class="result-label">Posters Loaded</div>
          </div>
        </div>

        <div class="result-card">
          <div class="result-icon">📁</div>
          <div class="result-content">
            <div class="result-number">{{ scanResult.directories_scanned || 0 }}</div>
            <div class="result-label">Directories</div>
          </div>
        </div>
      </div>

      <div v-if="scanResult.features" class="features-list mt-4">
        <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          ✨ Scan Features:
        </h5>
        <ul class="feature-items">
          <li v-for="feature in scanResult.features" :key="feature" class="feature-item">
            ✅ {{ feature }}
          </li>
        </ul>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <div class="error-icon">❌</div>
      <div class="error-content">
        <div class="error-title">Scan Failed</div>
        <div class="error-details">{{ error }}</div>
      </div>
    </div>

    <div class="scanner-info mt-6">
      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        ℹ️ About Media Scanning:
      </h5>
      <ul class="info-list">
        <li>🔍 Discovers new video and audio files in media directories</li>
        <li>🖼️ Automatically detects and loads poster.jpg files</li>
        <li>🎬 Extracts clean movie titles from filenames</li>
        <li>📁 Categorizes files based on directory structure</li>
        <li>💾 Stores poster images in database for fast loading</li>
        <li>🔄 Updates existing files when changes are detected</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { mediaApi } from '@/api/media'

const isScanning = ref(false)
const scanResult = ref<any>(null)
const error = ref<string | null>(null)

async function startScan() {
  isScanning.value = true
  error.value = null
  scanResult.value = null

  try {
    const response = await mediaApi.startScan()
    
    if (response.status === 'running') {
      scanResult.value = response
      
      // Simulate scan completion after a delay
      // In a real implementation, you'd poll for scan status
      setTimeout(() => {
        isScanning.value = false
        // You could add a status polling mechanism here
      }, 3000)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Scan failed'
    isScanning.value = false
  }
}
</script>

<style scoped>
.media-scanner {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6;
}

.scan-button {
  @apply px-6 py-3 rounded-lg font-medium transition-all duration-200;
}

.scan-button.idle {
  @apply bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg;
}

.scan-button.scanning {
  @apply bg-yellow-500 text-white cursor-not-allowed opacity-75;
}

.scan-button:disabled {
  @apply cursor-not-allowed opacity-50;
}

.results-grid {
  @apply grid grid-cols-2 md:grid-cols-4 gap-4 mb-4;
}

.result-card {
  @apply bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-center space-x-3;
}

.result-icon {
  @apply text-2xl;
}

.result-content {
  @apply flex-1;
}

.result-number {
  @apply text-2xl font-bold text-gray-900 dark:text-white;
}

.result-label {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.features-list {
  @apply bg-green-50 dark:bg-green-900/20 rounded-lg p-4;
}

.feature-items {
  @apply space-y-1;
}

.feature-item {
  @apply text-sm text-green-700 dark:text-green-300;
}

.error-message {
  @apply bg-red-50 dark:bg-red-900/20 rounded-lg p-4 flex items-start space-x-3;
}

.error-icon {
  @apply text-xl text-red-500;
}

.error-content {
  @apply flex-1;
}

.error-title {
  @apply font-medium text-red-800 dark:text-red-200;
}

.error-details {
  @apply text-sm text-red-600 dark:text-red-300 mt-1;
}

.info-list {
  @apply space-y-1;
}

.info-list li {
  @apply text-sm text-gray-600 dark:text-gray-400;
}
</style>
