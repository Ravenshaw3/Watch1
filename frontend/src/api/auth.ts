import apiClient from './client'
import type { User, LoginCredentials, RegisterData, AuthResponse, UserPreferences, UserPreferencesUpdate, ColorPalette } from '@/types/auth'

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/login', credentials)
    return response.data
  },

  async register(userData: RegisterData): Promise<User> {
    const response = await apiClient.post('/auth/register', userData)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put('/users/me', userData)
    return response.data
  },

  async getUserPreferences(): Promise<UserPreferences> {
    const response = await apiClient.get('/user/preferences')
    return response.data
  },

  async updateUserPreferences(preferences: UserPreferencesUpdate): Promise<UserPreferences> {
    const response = await apiClient.put('/user/preferences', preferences)
    return response.data
  },

  async getColorPalettes(): Promise<{ palettes: Array<{ name: string; colors: ColorPalette }> }> {
    const response = await apiClient.get('/user/preferences/color-palettes')
    return response.data
  },
}
