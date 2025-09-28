import apiClient from './client'

export interface MaintenanceJob {
  id: number
  job_name: string
  status: string
  details: Record<string, unknown> | null
  started_at: string
  finished_at: string | null
  duration_seconds: number | null
  result?: Record<string, unknown> | null
  running?: boolean
}

export interface QueuedJobResponse {
  job_id: number
  status: string
  submitted_at: string
}

export interface JobStatusResponse extends MaintenanceJob {
  running: boolean
}

export interface WorkerHealth {
  max_workers: number
  pending_jobs: number[]
  running: number
  completed_result_cache: number
}

export interface CleanOrphanPayload {
  apply?: boolean
  delete?: boolean
}

export interface PrunePayload extends CleanOrphanPayload {
  patterns?: string[]
}

export interface VerifyPosterPayload {
  rebuild?: boolean
}

export interface BackupPayload {
  format?: 'plain' | 'custom'
  output?: string
}

export const maintenanceApi = {
  async getDatabaseInfo() {
    const response = await apiClient.get('/admin/database/info')
    return response.data
  },

  async cleanOrphans(payload: CleanOrphanPayload = {}): Promise<QueuedJobResponse> {
    const response = await apiClient.post<QueuedJobResponse>('/admin/database/clean', payload)
    return response.data
  },

  async pruneTestMedia(payload: PrunePayload = {}): Promise<QueuedJobResponse> {
    const response = await apiClient.post<QueuedJobResponse>('/admin/database/prune', payload)
    return response.data
  },

  async verifyPosters(payload: VerifyPosterPayload = {}): Promise<QueuedJobResponse> {
    const response = await apiClient.post<QueuedJobResponse>('/admin/database/verify-posters', payload)
    return response.data
  },

  async createBackup(payload: BackupPayload = {}): Promise<QueuedJobResponse> {
    const response = await apiClient.post<QueuedJobResponse>('/admin/database/backup', payload)
    return response.data
  },

  async getJobHistory(limit = 20): Promise<{ jobs: MaintenanceJob[] }> {
    const response = await apiClient.get('/admin/database/jobs', {
      params: { limit }
    })
    return response.data
  },

  async getJobStatus(jobId: number): Promise<JobStatusResponse> {
    const response = await apiClient.get<JobStatusResponse>(`/admin/database/jobs/${jobId}`)
    return response.data
  },

  async cancelJob(jobId: number) {
    const response = await apiClient.delete<{ job_id: number; status: string }>(`/admin/database/jobs/${jobId}`)
    return response.data
  },

  async getWorkerHealth(): Promise<WorkerHealth> {
    const response = await apiClient.get<WorkerHealth>('/admin/worker/health')
    return response.data
  }
}
