/**
 * Subtitle API client for Watch1 Media Server
 */

import apiClient from './client'

export interface SubtitleInfo {
  id: string
  filename: string
  language: string
  format: string
  size: number
  url: string
}

export interface SubtitleTrack {
  src: string
  label: string
  language: string
  default?: boolean
}

/**
 * Get all subtitles for a media file
 */
export async function getMediaSubtitles(mediaId: string): Promise<SubtitleInfo[]> {
  try {
    const response = await apiClient.get(`/media/${mediaId}/subtitles`)
    return response.data
  } catch (error) {
    console.error('Failed to get media subtitles:', error)
    return []
  }
}

/**
 * Get subtitle file URL with authentication
 */
export function getSubtitleUrl(mediaId: string, filename: string): string {
  const token = localStorage.getItem('access_token')
  const baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'
  return `${baseUrl}/api/v1/media/${mediaId}/subtitles/${filename}?token=${token}`
}

/**
 * Convert SubtitleInfo to SubtitleTrack for video player
 */
export function convertToSubtitleTracks(subtitles: SubtitleInfo[], mediaId: string): SubtitleTrack[] {
  return subtitles.map((subtitle, index) => ({
    src: getSubtitleUrl(mediaId, subtitle.filename),
    label: getLanguageLabel(subtitle.language),
    language: subtitle.language,
    default: index === 0 // First subtitle as default
  }))
}

/**
 * Get human-readable language label
 */
function getLanguageLabel(languageCode: string): string {
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
    'th': 'Thai',
    'vi': 'Vietnamese',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'pl': 'Polish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'unknown': 'Unknown'
  }
  
  return languageMap[languageCode] || languageCode.toUpperCase()
}

/**
 * Check if subtitle file exists for media
 */
export async function hasSubtitles(mediaId: string): Promise<boolean> {
  try {
    const subtitles = await getMediaSubtitles(mediaId)
    return subtitles.length > 0
  } catch (error) {
    return false
  }
}

/**
 * Get preferred subtitle language from user settings
 */
export function getPreferredSubtitleLanguage(): string {
  return localStorage.getItem('preferred_subtitle_language') || 'en'
}

/**
 * Set preferred subtitle language in user settings
 */
export function setPreferredSubtitleLanguage(language: string): void {
  localStorage.setItem('preferred_subtitle_language', language)
}
