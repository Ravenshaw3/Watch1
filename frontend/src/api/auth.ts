import apiClient from './client'
import type { User, LoginCredentials, RegisterData, AuthResponse } from '@/types/auth'

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
}
