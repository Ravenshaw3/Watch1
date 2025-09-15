import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegisterData } from '@/types/auth'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_superuser || false)

  // Actions
  async function login(credentials: LoginCredentials) {
    isLoading.value = true
    try {
      const response = await authApi.login(credentials)
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      
      // Get user info
      await fetchUser()
      
      return response
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function register(userData: RegisterData) {
    isLoading.value = true
    try {
      const response = await authApi.register(userData)
      return response
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  async function fetchUser() {
    if (!token.value) return
    
    try {
      const response = await authApi.getCurrentUser()
      user.value = response
    } catch (error) {
      // Token might be invalid, clear it
      await logout()
      throw error
    }
  }

  async function initialize() {
    if (token.value) {
      try {
        await fetchUser()
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        await logout()
      }
    }
  }

  async function updateProfile(userData: Partial<User>) {
    if (!user.value) return
    
    try {
      const response = await authApi.updateProfile(userData)
      user.value = { ...user.value, ...response }
      return response
    } catch (error) {
      throw error
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    
    // Getters
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    register,
    logout,
    fetchUser,
    initialize,
    updateProfile
  }
})
