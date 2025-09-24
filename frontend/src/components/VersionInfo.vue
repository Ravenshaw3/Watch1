<template>
  <div class="version-info">
    <div class="flex items-center gap-2 text-sm text-gray-600">
      <span>Watch1 v{{ version }}</span>
      <button
        @click="showDetails = !showDetails"
        class="text-primary-600 hover:text-primary-700"
      >
        <InformationCircleIcon class="h-4 w-4" />
      </button>
    </div>
    
    <!-- Version Details Modal -->
    <div v-if="showDetails" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium">Version Information</h3>
          <button @click="showDetails = false" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
        
        <div class="space-y-3">
          <div>
            <span class="font-medium">Version:</span>
            <span class="ml-2">{{ version }}</span>
          </div>
          <div>
            <span class="font-medium">Build Date:</span>
            <span class="ml-2">{{ buildDate }}</span>
          </div>
          <div>
            <span class="font-medium">Features:</span>
            <ul class="mt-2 space-y-1">
              <li v-for="feature in features" :key="feature" class="text-sm text-gray-600">
                • {{ feature }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mediaApi } from '@/api/media'
import { InformationCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const showDetails = ref(false)
const version = ref('3.0.2')
const buildDate = ref('2025-09-22')
const features = ref<string[]>([
  'Unraid Production Deployment Ready',
  'CORS Policy Fixes',
  'Permissions-Policy Headers',
  'TypeScript Compatibility Resolved',
  'Authentication System Working',
  'Advanced Player Features',
  'Subtitle Support',
  'Picture-in-Picture Mode'
])

onMounted(async () => {
  try {
    const versionInfo = await mediaApi.getVersion()
    version.value = versionInfo.version
    buildDate.value = new Date(versionInfo.build_date).toLocaleDateString()
    features.value = versionInfo.features
  } catch (error) {
    console.error('Failed to load version info:', error)
  }
})
</script>
