<template>
  <div class="streaming-test-page">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <div class="test-header">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
          🎬 Media Streaming Test Suite
        </h1>
        <p class="text-gray-600 mb-8">
          Comprehensive testing for Watch1 media streaming capabilities
        </p>
      </div>

      <!-- Test Controls -->
      <div class="test-controls mb-8">
        <button 
          @click="runTests" 
          :disabled="isRunning"
          class="btn-primary mr-4"
        >
          <span v-if="isRunning">🧪 Running Tests...</span>
          <span v-else>🚀 Run All Tests</span>
        </button>
        
        <button 
          @click="clearResults"
          :disabled="isRunning"
          class="btn-outline"
        >
          🗑️ Clear Results
        </button>
      </div>

      <!-- Test Progress -->
      <div v-if="isRunning" class="test-progress mb-8">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
        <p class="text-sm text-gray-600 mt-2">
          {{ currentTest || 'Initializing tests...' }}
        </p>
      </div>

      <!-- Test Results -->
      <div v-if="testResults" class="test-results">
        <div class="results-summary mb-6">
          <div class="summary-card">
            <div class="summary-stat">
              <div class="stat-number text-green-600">{{ testResults.passed }}</div>
              <div class="stat-label">Passed</div>
            </div>
            <div class="summary-stat">
              <div class="stat-number text-red-600">{{ testResults.failed }}</div>
              <div class="stat-label">Failed</div>
            </div>
            <div class="summary-stat">
              <div class="stat-number text-blue-600">{{ testResults.total }}</div>
              <div class="stat-label">Total</div>
            </div>
            <div class="summary-stat">
              <div class="stat-number text-purple-600">{{ passRate }}%</div>
              <div class="stat-label">Pass Rate</div>
            </div>
          </div>
        </div>

        <!-- Detailed Results -->
        <div class="detailed-results">
          <h3 class="text-xl font-semibold mb-4">📋 Detailed Results</h3>
          <div class="results-list">
            <div 
              v-for="detail in testResults.details" 
              :key="detail.name"
              :class="['result-item', detail.status === 'PASS' ? 'success' : 'failure']"
            >
              <div class="result-header">
                <span class="result-icon">
                  {{ detail.status === 'PASS' ? '✅' : '❌' }}
                </span>
                <span class="result-name">{{ detail.name }}</span>
                <span v-if="detail.duration" class="result-duration">
                  {{ detail.duration }}ms
                </span>
              </div>
              <div class="result-message">
                {{ detail.message }}
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations mt-8">
          <h3 class="text-xl font-semibold mb-4">🎯 Recommendations</h3>
          <div class="recommendation-card">
            <div v-if="testResults.failed === 0" class="success-message">
              <h4 class="font-semibold text-green-800 mb-2">
                🎉 All Tests Passed!
              </h4>
              <p class="text-green-700">
                Your media streaming is working perfectly. You can now:
              </p>
              <ul class="mt-2 text-green-700">
                <li>• Browse and play videos from the Library</li>
                <li>• Use quality selection and subtitle features</li>
                <li>• Test with different video formats and sizes</li>
                <li>• Monitor performance with the analytics dashboard</li>
              </ul>
            </div>
            
            <div v-else class="failure-message">
              <h4 class="font-semibold text-red-800 mb-2">
                ⚠️ Some Tests Failed
              </h4>
              <p class="text-red-700 mb-2">
                Please check the following:
              </p>
              <ul class="text-red-700">
                <li>• Backend API is running on http://localhost:8000</li>
                <li>• You are logged in with valid credentials</li>
                <li>• Database contains media files</li>
                <li>• Network connectivity between frontend and backend</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions mt-8">
          <h3 class="text-xl font-semibold mb-4">🚀 Quick Actions</h3>
          <div class="action-buttons">
            <router-link to="/library" class="btn-primary">
              📚 Go to Library
            </router-link>
            <router-link to="/settings" class="btn-outline">
              ⚙️ Settings
            </router-link>
            <button @click="openConsole" class="btn-outline">
              🔍 Open Console
            </button>
          </div>
        </div>
      </div>

      <!-- Manual Test Section -->
      <div class="manual-tests mt-12">
        <h2 class="text-2xl font-bold mb-4">🎮 Manual Testing</h2>
        <div class="manual-test-grid">
          <div class="manual-test-card">
            <h3 class="font-semibold mb-2">🎬 Video Playback</h3>
            <p class="text-sm text-gray-600 mb-3">
              Test actual video streaming and controls
            </p>
            <router-link to="/library" class="btn-sm btn-primary">
              Test Now
            </router-link>
          </div>
          
          <div class="manual-test-card">
            <h3 class="font-semibold mb-2">🎛️ Quality Selection</h3>
            <p class="text-sm text-gray-600 mb-3">
              Test video quality switching during playback
            </p>
            <button @click="testQuality" class="btn-sm btn-outline">
              Test Quality
            </button>
          </div>
          
          <div class="manual-test-card">
            <h3 class="font-semibold mb-2">📝 Subtitles</h3>
            <p class="text-sm text-gray-600 mb-3">
              Test subtitle upload and display
            </p>
            <button @click="testSubtitles" class="btn-sm btn-outline">
              Test Subtitles
            </button>
          </div>
          
          <div class="manual-test-card">
            <h3 class="font-semibold mb-2">📊 Performance</h3>
            <p class="text-sm text-gray-600 mb-3">
              Monitor streaming performance and buffering
            </p>
            <button @click="testPerformance" class="btn-sm btn-outline">
              Test Performance
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { mediaStreamingTester } from '@/utils/mediaTest'

// State
const isRunning = ref(false)
const testResults = ref<any>(null)
const currentTest = ref('')
const progressPercentage = ref(0)

// Computed
const passRate = computed(() => {
  if (!testResults.value) return 0
  return Math.round((testResults.value.passed / testResults.value.total) * 100)
})

// Methods
const runTests = async () => {
  isRunning.value = true
  currentTest.value = 'Initializing tests...'
  progressPercentage.value = 0
  
  try {
    // Simulate progress updates
    const progressInterval = setInterval(() => {
      if (progressPercentage.value < 90) {
        progressPercentage.value += 10
      }
    }, 500)
    
    const results = await mediaStreamingTester.runAllTests()
    
    clearInterval(progressInterval)
    progressPercentage.value = 100
    currentTest.value = 'Tests completed!'
    
    setTimeout(() => {
      testResults.value = results
      isRunning.value = false
      currentTest.value = ''
      progressPercentage.value = 0
    }, 500)
    
  } catch (error) {
    console.error('Test execution failed:', error)
    isRunning.value = false
    currentTest.value = ''
    progressPercentage.value = 0
  }
}

const clearResults = () => {
  testResults.value = null
}

const openConsole = () => {
  console.log('🎬 Watch1 Media Streaming Test Console')
  console.log('Run window.testMediaStreaming() to execute tests from console')
  alert('Check the browser console for testing utilities!')
}

const testQuality = () => {
  alert('Navigate to Library → Play a video → Click HD button to test quality selection')
}

const testSubtitles = () => {
  alert('Navigate to Library → Play a video → Click CC button to test subtitles')
}

const testPerformance = () => {
  alert('Navigate to Library → Play a large video file → Monitor loading and buffering')
}
</script>

<style scoped>
.streaming-test-page {
  min-height: 100vh;
  background: #f9fafb;
}

.test-header {
  text-align: center;
  margin-bottom: 2rem;
}

.test-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn-primary {
  @apply bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors;
}

.btn-sm {
  @apply px-4 py-2 text-sm rounded-md font-medium transition-colors;
}

.btn-sm.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-sm.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.test-progress {
  max-width: 500px;
  margin: 0 auto;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.results-summary {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.summary-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 2rem;
}

.summary-stat {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.detailed-results {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.result-item.success {
  background: #f0fdf4;
  border-left-color: #22c55e;
}

.result-item.failure {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.result-name {
  font-weight: 600;
  flex: 1;
}

.result-duration {
  font-size: 0.875rem;
  color: #6b7280;
}

.result-message {
  font-size: 0.875rem;
  color: #6b7280;
}

.recommendations {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.recommendation-card {
  padding: 1.5rem;
  border-radius: 8px;
}

.success-message {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.failure-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.manual-tests {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.manual-test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.manual-test-card {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}
</style>
