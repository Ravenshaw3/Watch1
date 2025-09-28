import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  maintenanceApi,
  type MaintenanceJob,
  type QueuedJobResponse,
  type JobStatusResponse,
  type WorkerHealth
} from '@/api/maintenance'

type ResultStatus = 'success' | 'failed' | 'cancelled' | null

interface MaintenanceState {
  databaseInfo: Record<string, unknown> | null
  jobs: MaintenanceJob[]
  isLoading: boolean
  error: string | null
  activeAction: string | null
  actionMessage: string | null
  currentJobId: number | null
  currentJobStatus: JobStatusResponse | null
  lastResultStatus: ResultStatus
  lastResultMessage: string | null
  workerHealth: WorkerHealth | null
}

interface PollMessages {
  successMessage: string
  failureMessage: string
  cancelMessage: string
}

const POLL_INTERVAL_MS = 3000

let pollTimer: number | null = null
let currentPollMessages: PollMessages | null = null

export const useMaintenanceStore = defineStore('maintenance', () => {
  const state = ref<MaintenanceState>({
    databaseInfo: null,
    jobs: [],
    isLoading: false,
    error: null,
    activeAction: null,
    actionMessage: null,
    currentJobId: null,
    currentJobStatus: null,
    lastResultStatus: null,
    lastResultMessage: null,
    workerHealth: null
  })

  function clearPolling() {
    if (pollTimer !== null) {
      window.clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function updateWorkerHealth() {
    try {
      state.value.workerHealth = await maintenanceApi.getWorkerHealth()
    } catch (error: unknown) {
      state.value.workerHealth = null
      // Suppress authorization failures silently, but surface other errors
      const status = (error as any)?.response?.status
      if (status && status !== 401 && status !== 403) {
        state.value.error = 'Failed to fetch worker health.'
        throw error
      }
    }
  }

  function startAction(name: string, message: string) {
    state.value.activeAction = name
    state.value.actionMessage = message
    state.value.error = null
    state.value.lastResultStatus = null
    state.value.lastResultMessage = null
  }

  function finishAction(resultStatus: ResultStatus = null, message: string | null = null) {
    clearPolling()
    state.value.currentJobId = null
    state.value.currentJobStatus = null
    state.value.activeAction = null
    state.value.actionMessage = null
    state.value.lastResultStatus = resultStatus
    state.value.lastResultMessage = message
    currentPollMessages = null
  }

  async function fetchDatabaseInfo() {
    state.value.isLoading = true
    state.value.error = null
    try {
      const info = await maintenanceApi.getDatabaseInfo()
      state.value.databaseInfo = info
    } catch (error) {
      state.value.error = 'Failed to load database information.'
      throw error
    } finally {
      state.value.isLoading = false
    }
  }

  async function fetchJobs(limit = 20) {
    state.value.error = null
    try {
      const response = await maintenanceApi.getJobHistory(limit)
      state.value.jobs = response.jobs
    } catch (error) {
      state.value.error = 'Failed to load job history.'
      throw error
    }
  }

  async function refreshJobStatus(jobId: number) {
    if (!jobId) return
    try {
      const status = await maintenanceApi.getJobStatus(jobId)
      state.value.currentJobStatus = status

      if (!status.running && status.status !== 'running') {
        const messages = currentPollMessages
        clearPolling()
        await fetchJobs().catch(() => undefined)
        await updateWorkerHealth().catch(() => undefined)

        if (status.status === 'success') {
          finishAction('success', messages?.successMessage ?? 'Maintenance job completed successfully.')
        } else if (status.status === 'cancelled') {
          finishAction('cancelled', messages?.cancelMessage ?? 'Maintenance job cancelled.')
        } else {
          state.value.error = messages?.failureMessage ?? 'Maintenance job failed.'
          finishAction('failed', messages?.failureMessage ?? 'Maintenance job failed.')
        }
      }
    } catch (error) {
      const messages = currentPollMessages
      clearPolling()
      state.value.error = messages?.failureMessage ?? 'Failed to fetch job status.'
      finishAction('failed', messages?.failureMessage ?? 'Maintenance job failed.')
      throw error
    }
  }

  async function beginPolling(jobId: number, messages: PollMessages) {
    currentPollMessages = messages
    state.value.currentJobId = jobId
    state.value.currentJobStatus = null

    clearPolling()
    await refreshJobStatus(jobId).catch(() => undefined)
    await updateWorkerHealth().catch(() => undefined)

    pollTimer = window.setInterval(() => {
      refreshJobStatus(jobId).catch((error) => {
        console.error('Maintenance polling error', error)
        clearPolling()
      })
      updateWorkerHealth().catch(() => undefined)
    }, POLL_INTERVAL_MS)
  }

  interface QueueOptions {
    actionName: string
    startMessage: string
    request: () => Promise<QueuedJobResponse>
    successMessage: string
    failureMessage: string
    cancelMessage?: string
  }

  async function queueJob({
    actionName,
    startMessage,
    request,
    successMessage,
    failureMessage,
    cancelMessage = 'Maintenance job cancelled.'
  }: QueueOptions) {
    startAction(actionName, startMessage)
    try {
      const queued = await request()
      await beginPolling(queued.job_id, {
        successMessage,
        failureMessage,
        cancelMessage
      })
      return queued
    } catch (error) {
      finishAction('failed', failureMessage)
      state.value.error = failureMessage
      throw error
    }
  }

  async function cleanOrphans(apply = false, deleteRows = false) {
    return queueJob({
      actionName: 'clean-orphans',
      startMessage: apply
        ? deleteRows
          ? 'Deleting orphan records…'
          : 'Marking orphan records deleted…'
        : 'Checking for orphan records…',
      request: () => maintenanceApi.cleanOrphans({ apply, delete: deleteRows }),
      successMessage: 'Orphan clean completed.',
      failureMessage: 'Failed to clean orphan records.',
      cancelMessage: 'Orphan clean cancelled.'
    })
  }

  async function pruneTestMedia(apply = false, deleteRows = false, patterns?: string[]) {
    return queueJob({
      actionName: 'prune-test-media',
      startMessage: apply
        ? deleteRows
          ? 'Deleting test media…'
          : 'Marking test media deleted…'
        : 'Scanning for test media…',
      request: () => maintenanceApi.pruneTestMedia({ apply, delete: deleteRows, patterns }),
      successMessage: 'Test media prune completed.',
      failureMessage: 'Failed to prune test media.',
      cancelMessage: 'Test media prune cancelled.'
    })
  }

  async function verifyPosters(rebuild = false) {
    return queueJob({
      actionName: 'verify-posters',
      startMessage: rebuild ? 'Rebuilding missing posters…' : 'Verifying poster data…',
      request: () => maintenanceApi.verifyPosters({ rebuild }),
      successMessage: 'Poster verification completed.',
      failureMessage: 'Failed to verify poster data.',
      cancelMessage: 'Poster verification cancelled.'
    })
  }

  async function createBackup(format: 'plain' | 'custom' = 'plain', output?: string) {
    return queueJob({
      actionName: 'create-backup',
      startMessage: format === 'custom' ? 'Creating custom backup…' : 'Creating plain backup…',
      request: () => maintenanceApi.createBackup({ format, output }),
      successMessage: 'Backup completed.',
      failureMessage: 'Failed to create database backup.',
      cancelMessage: 'Backup cancelled.'
    })
  }

  async function cancelCurrentJob() {
    if (!state.value.currentJobId) return
    try {
      await maintenanceApi.cancelJob(state.value.currentJobId)
      await refreshJobStatus(state.value.currentJobId)
    } catch (error: unknown) {
      const detail = (error as any)?.response?.data?.detail
      state.value.error = detail ?? 'Unable to cancel job.'
      throw error
    }
  }

  function stopPolling() {
    clearPolling()
  }

  return {
    state,
    fetchDatabaseInfo,
    fetchJobs,
    updateWorkerHealth,
    cleanOrphans,
    pruneTestMedia,
    verifyPosters,
    createBackup,
    cancelCurrentJob,
    stopPolling
  }
})
