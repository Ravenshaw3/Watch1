<template>
  <div class="subtitle-manager">
    <div class="manager-header">
      <h2 class="manager-title">Subtitle Management</h2>
      <button @click="showUploader = !showUploader" class="btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Add Subtitles
      </button>
    </div>

    <!-- Subtitle Uploader -->
    <div v-if="showUploader" class="uploader-section">
      <SubtitleUploader 
        :media-id="mediaId" 
        @uploaded="onSubtitlesUploaded"
        @error="onUploadError"
      />
    </div>

    <!-- Existing Subtitles -->
    <div class="subtitles-section">
      <h3 class="section-title">Available Subtitles</h3>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading subtitles...</p>
      </div>
      
      <div v-else-if="subtitles.length === 0" class="empty-state">
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM6 6v12h12V6H6zm3 3a1 1 0 011-1h4a1 1 0 110 2h-4a1 1 0 01-1-1zm0 4a1 1 0 011-1h4a1 1 0 110 2h-4a1 1 0 01-1-1z"/>
        </svg>
        <p class="empty-text">No subtitles available</p>
        <p class="empty-subtext">Upload subtitle files to get started</p>
      </div>
      
      <div v-else class="subtitle-list">
        <div v-for="subtitle in subtitles" :key="subtitle.id" class="subtitle-item">
          <div class="subtitle-info">
            <div class="subtitle-main">
              <span class="subtitle-filename">{{ subtitle.filename }}</span>
              <span class="subtitle-language">{{ getLanguageLabel(subtitle.language) }}</span>
            </div>
            <div class="subtitle-meta">
              <span class="subtitle-format">{{ subtitle.format.toUpperCase() }}</span>
              <span class="subtitle-size">{{ formatFileSize(subtitle.size) }}</span>
            </div>
          </div>
          
          <div class="subtitle-actions">
            <button @click="downloadSubtitle(subtitle)" class="action-btn" title="Download">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
              </svg>
            </button>
            <button @click="showSubtitlePreview(subtitle)" class="action-btn" title="Preview">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
            <button @click="deleteSubtitle(subtitle)" class="action-btn delete-btn" title="Delete">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subtitle Preview Modal -->
    <div v-if="showPreview" class="preview-modal" @click="closePreview">
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h3>{{ previewSubtitleRef?.filename }}</h3>
          <button @click="closePreview" class="close-btn">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="preview-body">
          <pre class="subtitle-content">{{ previewContent }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMediaSubtitles, type SubtitleInfo } from '@/api/subtitles'
import SubtitleUploader from './SubtitleUploader.vue'

interface Props {
  mediaId: string
}

const props = defineProps<Props>()

// Reactive state
const subtitles = ref<SubtitleInfo[]>([])
const loading = ref(false)
const showUploader = ref(false)
const showPreview = ref(false)
const previewSubtitleRef = ref<SubtitleInfo | null>(null)
const previewContent = ref('')

// Methods
const loadSubtitles = async () => {
  loading.value = true
  try {
    subtitles.value = await getMediaSubtitles(props.mediaId)
  } catch (error) {
    console.error('Failed to load subtitles:', error)
  } finally {
    loading.value = false
  }
}

const onSubtitlesUploaded = (uploadedSubtitles: SubtitleInfo[]) => {
  subtitles.value.push(...uploadedSubtitles)
  showUploader.value = false
}

const onUploadError = (message: string) => {
  alert(`Upload failed: ${message}`)
}

const downloadSubtitle = (subtitle: SubtitleInfo) => {
  const link = document.createElement('a')
  link.href = `http://localhost:8000${subtitle.url}?token=${localStorage.getItem('access_token')}`
  link.download = subtitle.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const showSubtitlePreview = async (subtitle: SubtitleInfo) => {
  try {
    const response = await fetch(`http://localhost:8000${subtitle.url}?token=${localStorage.getItem('access_token')}`)
    const content = await response.text()
    
    // Limit preview to first 2000 characters
    previewContent.value = content.length > 2000 ? content.substring(0, 2000) + '...' : content
    previewSubtitleRef.value = subtitle
    showPreview.value = true
  } catch (error) {
    alert('Failed to load subtitle preview')
  }
}

const closePreview = () => {
  showPreview.value = false
  previewSubtitleRef.value = null
  previewContent.value = ''
}

const deleteSubtitle = async (subtitle: SubtitleInfo) => {
  if (!confirm(`Are you sure you want to delete "${subtitle.filename}"?`)) {
    return
  }
  
  try {
    const response = await fetch(`http://localhost:8000/api/v1/media/${props.mediaId}/subtitles/${subtitle.filename}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.ok) {
      subtitles.value = subtitles.value.filter(s => s.id !== subtitle.id)
    } else {
      throw new Error('Delete failed')
    }
  } catch (error) {
    alert('Failed to delete subtitle')
  }
}

const getLanguageLabel = (languageCode: string): string => {
  const languageMap: Record<string, string> = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'unknown': 'Unknown'
  }
  
  return languageMap[languageCode] || languageCode.toUpperCase()
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Lifecycle
onMounted(() => {
  loadSubtitles()
})
</script>

<style scoped>
.subtitle-manager {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.manager-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.btn-primary {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background: #2563eb;
}

.uploader-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.subtitles-section {
  margin-top: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  color: #6b7280;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: #d1d5db;
}

.empty-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.empty-subtext {
  font-size: 0.875rem;
}

.subtitle-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.subtitle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.subtitle-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.subtitle-info {
  flex: 1;
}

.subtitle-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.25rem;
}

.subtitle-filename {
  font-weight: 500;
  color: #111827;
}

.subtitle-language {
  padding: 0.25rem 0.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.subtitle-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.subtitle-format {
  font-weight: 500;
}

.subtitle-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #e5e7eb;
}

.delete-btn {
  color: #ef4444;
}

.delete-btn:hover {
  background: #fee2e2;
  border-color: #fecaca;
}

.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.preview-content {
  background: white;
  border-radius: 8px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.preview-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f3f4f6;
}

.preview-body {
  padding: 1rem;
  overflow: auto;
  max-height: 70vh;
}

.subtitle-content {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  color: #374151;
  margin: 0;
}
</style>
