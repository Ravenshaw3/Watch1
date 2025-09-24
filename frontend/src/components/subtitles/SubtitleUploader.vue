<template>
  <div class="subtitle-uploader">
    <div class="upload-area" :class="{ 'drag-over': isDragOver }" 
         @drop="handleDrop" 
         @dragover.prevent="isDragOver = true" 
         @dragleave="isDragOver = false"
         @click="triggerFileInput">
      <input 
        ref="fileInput" 
        type="file" 
        accept=".srt,.vtt,.ass,.ssa,.sub" 
        multiple 
        @change="handleFileSelect" 
        class="hidden"
      />
      
      <div class="upload-content">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
        </svg>
        <p class="upload-text">
          Drop subtitle files here or <span class="upload-link">click to browse</span>
        </p>
        <p class="upload-formats">
          Supported formats: SRT, VTT, ASS, SSA, SUB
        </p>
      </div>
    </div>

    <!-- File List -->
    <div v-if="selectedFiles.length > 0" class="file-list">
      <h3 class="file-list-title">Selected Files</h3>
      <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
        
        <div class="file-language">
          <label class="language-label">Language:</label>
          <select v-model="file.language" class="language-select">
            <option value="">Auto-detect</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese</option>
            <option value="ru">Russian</option>
            <option value="zh">Chinese</option>
            <option value="ja">Japanese</option>
            <option value="ko">Korean</option>
            <option value="ar">Arabic</option>
            <option value="hi">Hindi</option>
          </select>
        </div>
        
        <button @click="removeFile(index)" class="remove-btn" title="Remove file">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Upload Actions -->
    <div v-if="selectedFiles.length > 0" class="upload-actions">
      <button @click="clearFiles" class="btn-secondary">Clear All</button>
      <button @click="uploadFiles" :disabled="isUploading" class="btn-primary">
        <span v-if="isUploading">Uploading...</span>
        <span v-else>Upload Subtitles</span>
      </button>
    </div>

    <!-- Upload Progress -->
    <div v-if="isUploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <p class="progress-text">{{ uploadProgress }}% complete</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface SubtitleFile extends File {
  language?: string
}

interface Props {
  mediaId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  uploaded: [subtitles: any[]]
  error: [message: string]
}>()

// Reactive state
const fileInput = ref<HTMLInputElement>()
const selectedFiles = ref<SubtitleFile[]>([])
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
  
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

const addFiles = (files: File[]) => {
  const subtitleFiles = files.filter(file => {
    const ext = file.name.toLowerCase().split('.').pop()
    return ['srt', 'vtt', 'ass', 'ssa', 'sub'].includes(ext || '')
  })
  
  subtitleFiles.forEach(file => {
    const subtitleFile = file as SubtitleFile
    subtitleFile.language = detectLanguageFromFilename(file.name)
    selectedFiles.value.push(subtitleFile)
  })
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const clearFiles = () => {
  selectedFiles.value = []
}

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return
  
  isUploading.value = true
  uploadProgress.value = 0
  
  try {
    const uploadedSubtitles = []
    
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i]
      
      // Create FormData
      const formData = new FormData()
      formData.append('file', file)
      if (file.language) {
        formData.append('language', file.language)
      }
      
      // Upload file
      const response = await fetch(`http://localhost:8000/api/v1/media/${props.mediaId}/subtitles`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      })
      
      if (response.ok) {
        const subtitle = await response.json()
        uploadedSubtitles.push(subtitle)
      } else {
        throw new Error(`Failed to upload ${file.name}`)
      }
      
      // Update progress
      uploadProgress.value = Math.round(((i + 1) / selectedFiles.value.length) * 100)
    }
    
    emit('uploaded', uploadedSubtitles)
    selectedFiles.value = []
    
  } catch (error) {
    emit('error', error instanceof Error ? error.message : 'Upload failed')
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

const detectLanguageFromFilename = (filename: string): string => {
  const name = filename.toLowerCase()
  
  // Common language patterns
  if (name.includes('.en.') || name.includes('english')) return 'en'
  if (name.includes('.es.') || name.includes('spanish')) return 'es'
  if (name.includes('.fr.') || name.includes('french')) return 'fr'
  if (name.includes('.de.') || name.includes('german')) return 'de'
  if (name.includes('.it.') || name.includes('italian')) return 'it'
  if (name.includes('.pt.') || name.includes('portuguese')) return 'pt'
  if (name.includes('.ru.') || name.includes('russian')) return 'ru'
  if (name.includes('.zh.') || name.includes('chinese')) return 'zh'
  if (name.includes('.ja.') || name.includes('japanese')) return 'ja'
  if (name.includes('.ko.') || name.includes('korean')) return 'ko'
  
  return ''
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.subtitle-uploader {
  max-width: 600px;
  margin: 0 auto;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #3b82f6;
  background: #eff6ff;
}

.hidden {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: #6b7280;
}

.upload-text {
  font-size: 1.1rem;
  color: #374151;
  margin: 0;
}

.upload-link {
  color: #3b82f6;
  font-weight: 500;
}

.upload-formats {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.file-list {
  margin-top: 2rem;
}

.file-list-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #374151;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 500;
  color: #374151;
}

.file-size {
  font-size: 0.875rem;
  color: #6b7280;
}

.file-language {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.language-label {
  font-size: 0.875rem;
  color: #374151;
}

.language-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.remove-btn {
  padding: 0.5rem;
  color: #ef4444;
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.remove-btn:hover {
  background: #fee2e2;
}

.upload-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-progress {
  margin-top: 1rem;
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

.progress-text {
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>
