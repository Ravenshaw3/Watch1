<template>
  <div class="scan-info bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-medium text-gray-900">Media Library Status</h3>
      <button
        @click="refreshInfo"
        :disabled="isLoading"
        class="text-primary-600 hover:text-primary-700 disabled:opacity-50"
      >
        <ArrowPathIcon class="h-5 w-5" :class="{ 'animate-spin': isLoading }" />
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Directory Information -->
      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-3">Scan Directory</h4>
        <div class="space-y-2 text-sm">
          <div class="flex items-center">
            <FolderIcon class="h-4 w-4 text-gray-400 mr-2" />
            <span class="text-gray-600">{{ scanInfo.directory_info?.scan_directory || 'Not available' }}</span>
          </div>
          <div class="flex items-center">
            <CheckCircleIcon v-if="scanInfo.directory_info?.scan_directory_exists" class="h-4 w-4 text-green-500 mr-2" />
            <XCircleIcon v-else class="h-4 w-4 text-red-500 mr-2" />
            <span :class="scanInfo.directory_info?.scan_directory_exists ? 'text-green-600' : 'text-red-600'">
              {{ scanInfo.directory_info?.scan_directory_exists ? 'Directory exists' : 'Directory not found' }}
            </span>
          </div>
          <div v-if="scanInfo.directory_info?.total_files_in_directory !== undefined" class="text-gray-600">
            📁 {{ scanInfo.directory_info.total_files_in_directory }} total files
          </div>
          <div v-if="scanInfo.directory_info?.media_files_in_directory !== undefined" class="text-gray-600">
            🎬 {{ scanInfo.directory_info.media_files_in_directory }} media files
          </div>
        </div>
      </div>
      
      <!-- Library Statistics -->
      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-3">Library Statistics</h4>
        <div class="space-y-2 text-sm">
          <div class="flex items-center">
            <FilmIcon class="h-4 w-4 text-gray-400 mr-2" />
            <span class="text-gray-600">{{ scanInfo.library_stats?.total_media_files || 0 }} files in library</span>
          </div>
          <div class="flex items-center">
            <ServerIcon class="h-4 w-4 text-gray-400 mr-2" />
            <span class="text-gray-600">{{ scanInfo.library_stats?.total_size_formatted || '0 Bytes' }} total size</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Category Breakdown -->
    <div v-if="scanInfo.library_stats?.categories" class="mt-6">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Categories</h4>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        <div
          v-for="(category, name) in scanInfo.library_stats.categories"
          :key="name"
          class="bg-gray-50 rounded-lg p-3 text-center"
        >
          <div class="text-lg font-semibold text-gray-900">{{ category.count }}</div>
          <div class="text-xs text-gray-600">{{ category.display_name }}</div>
        </div>
      </div>
    </div>
    
    <!-- Supported Extensions -->
    <div v-if="scanInfo.directory_info?.supported_extensions" class="mt-6">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Supported File Types</h4>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="ext in scanInfo.directory_info.supported_extensions"
          :key="ext"
          class="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded"
        >
          {{ ext }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mediaApi } from '@/api/media'
import { 
  ArrowPathIcon, 
  FolderIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  FilmIcon, 
  ServerIcon 
} from '@heroicons/vue/24/outline'

const scanInfo = ref<any>({})
const isLoading = ref(false)

async function loadScanInfo() {
  isLoading.value = true
  try {
    scanInfo.value = await mediaApi.getScanInfo()
  } catch (error) {
    console.error('Failed to load scan info:', error)
  } finally {
    isLoading.value = false
  }
}

async function refreshInfo() {
  await loadScanInfo()
}

onMounted(() => {
  loadScanInfo()
})

// Expose refresh function for parent components
defineExpose({
  refreshInfo
})
</script>

