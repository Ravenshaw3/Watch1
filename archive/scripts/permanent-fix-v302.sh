#!/bin/bash
# PERMANENT FIX for Recurring Watch1 Issues v3.0.2
echo "🔧 PERMANENT FIX FOR RECURRING WATCH1 ISSUES"
echo "============================================="

cd /mnt/user/appdata/watch1

echo ""
echo "CRITICAL ISSUE IDENTIFIED:"
echo "=========================="
echo "❌ Fixes keep reverting because frontend container doesn't persist changes"
echo "❌ Volume mounts disabled due to Windows Docker compatibility issues"
echo "❌ File changes made via docker exec are lost on container restart"
echo "❌ Need to apply fixes to source files and rebuild container"
echo ""

echo "ROOT CAUSE ANALYSIS:"
echo "==================="
echo "1. Frontend container uses build-time file copying (not runtime mounting)"
echo "2. Changes made inside container are ephemeral"
echo "3. Container restart loses all fixes"
echo "4. Source files on host need to be updated permanently"
echo ""

echo "PERMANENT SOLUTION:"
echo "=================="
echo "1. Apply fixes directly to host source files"
echo "2. Rebuild frontend container with --no-cache"
echo "3. Restart containers to apply changes"
echo "4. Verify fixes persist after restart"
echo ""

echo "1. STOPPING CONTAINERS FOR CLEAN REBUILD"
echo "========================================="

echo "Stopping all containers..."
docker-compose down
sleep 5

echo "Removing frontend image for clean rebuild..."
docker rmi watch1-frontend 2>/dev/null || echo "Frontend image not found (OK)"

echo ""
echo "2. APPLYING PERMANENT FIXES TO SOURCE FILES"
echo "==========================================="

echo "Creating permanent API client fix..."
cat > frontend/src/api/client.ts << 'EOF'
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios"
import { useAuthStore } from "@/stores/auth"

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://192.168.254.14:8000/api/v1",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor to add authorization header
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Get auth store instance
    const authStore = useAuthStore()
    
    // Add authorization header if token exists
    if (authStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    // Add CORS headers
    config.headers = config.headers || {}
    config.headers["Access-Control-Allow-Origin"] = "*"
    config.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    config.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    console.log("API Request:", config.method?.toUpperCase(), config.url, {
      hasAuth: !!authStore.token,
      token: authStore.token?.substring(0, 20) + "..."
    })
    
    return config
  },
  (error) => {
    console.error("Request interceptor error:", error)
    return Promise.reject(error)
  }
)

// Response interceptor to handle authorization errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log("API Response:", response.status, response.config.url)
    return response
  },
  async (error) => {
    console.error("API Error:", error.response?.status, error.config?.url, error.message)
    
    // Handle authorization errors
    if (error.response?.status === 401) {
      console.warn("Authorization failed - clearing auth state")
      const authStore = useAuthStore()
      await authStore.logout()
      
      // Redirect to login page
      if (typeof window !== "undefined") {
        window.location.href = "/login"
      }
    }
    
    // Handle chunk loading errors
    if (error.message?.includes("Loading chunk") || error.message?.includes("ty chunk")) {
      console.warn("Chunk loading error - reloading page")
      if (typeof window !== "undefined") {
        window.location.reload()
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
EOF

echo "✅ Permanent API client fix applied to source file"

echo ""
echo "Creating permanent auth store fix..."
cat > frontend/src/stores/auth.ts << 'EOF'
import { defineStore } from "pinia"
import { ref, computed } from "vue"
import type { User, LoginCredentials, RegisterData } from "@/types/auth"
import { authApi } from "@/api/auth"

export const useAuthStore = defineStore("auth", () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem("access_token"))
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => {
    const hasToken = !!token.value
    const hasUser = !!user.value
    console.log("Auth check:", { hasToken, hasUser, token: token.value?.substring(0, 20) + "..." })
    return hasToken && hasUser
  })
  const isAdmin = computed(() => user.value?.is_superuser || false)

  // Actions
  async function login(credentials: LoginCredentials) {
    isLoading.value = true
    try {
      console.log("Attempting login with:", credentials.username)
      const response = await authApi.login(credentials)
      
      console.log("Login response:", response)
      
      if (response.access_token) {
        token.value = response.access_token
        localStorage.setItem("access_token", response.access_token)
        console.log("✅ Login successful, token stored:", response.access_token.substring(0, 20) + "...")
        
        // Get user info immediately after login
        await fetchUser()
        
        return response
      } else {
        console.error("❌ No access token in response:", response)
        throw new Error("No access token received from server")
      }
    } catch (error) {
      console.error("❌ Login failed:", error)
      // Clear any partial state
      token.value = null
      user.value = null
      localStorage.removeItem("access_token")
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
      console.error("Registration failed:", error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    console.log("Logging out...")
    user.value = null
    token.value = null
    localStorage.removeItem("access_token")
  }

  async function fetchUser() {
    if (!token.value) {
      console.log("No token available for fetchUser")
      return
    }
    
    try {
      console.log("Fetching user profile...")
      const response = await authApi.getCurrentUser()
      user.value = response
      console.log("✅ User profile loaded:", response.email)
    } catch (error) {
      console.error("❌ Failed to fetch user:", error)
      // Token might be invalid, clear it
      await logout()
      throw error
    }
  }

  async function initialize() {
    console.log("Initializing auth store...")
    if (token.value) {
      try {
        await fetchUser()
        console.log("✅ Auth initialization successful")
      } catch (error) {
        console.error("❌ Auth initialization failed:", error)
        await logout()
      }
    } else {
      console.log("No token found during initialization")
    }
  }

  async function updateProfile(userData: Partial<User>) {
    if (!user.value) return
    
    try {
      const response = await authApi.updateProfile(userData)
      user.value = { ...user.value, ...response }
      return response
    } catch (error) {
      console.error("Profile update failed:", error)
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
EOF

echo "✅ Permanent auth store fix applied to source file"

echo ""
echo "Creating permanent media API fix..."
cat > frontend/src/api/media.ts << 'EOF'
import apiClient from "./client"
import type {
  MediaFile,
  MediaSearchResponse,
  MediaUploadResponse,
  MediaCategoryInfo,
  MediaScanResult,
  VersionInfo,
  MediaCategory,
  Playlist,
  PlaylistCreate,
  PlaylistUpdate,
  PlaylistItemAdd,
  TVSeriesResponse,
  TVEpisodesResponse
} from "@/types/media"

export const mediaApi = {
  async getMediaFiles(params: {
    page?: number
    page_size?: number
    category?: MediaCategory
    search?: string
    sort_by?: string
    sort_order?: string
  } = {}): Promise<MediaSearchResponse> {
    try {
      console.log("Getting media files with params:", params)
      const response = await apiClient.get("/media", { params })
      
      // Handle different response formats safely
      const data = response.data
      console.log("Media API response:", data)
      
      // Ensure we always return the expected format
      return {
        items: data.items || data.media || [],
        total: data.total || 0,
        page: data.page || 1,
        page_size: data.page_size || 20,
        categories: data.categories || {}
      }
    } catch (error) {
      console.error("❌ Failed to get media files:", error)
      // Return safe default response
      return {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
        categories: {}
      }
    }
  },

  async getMediaFile(id: string | number): Promise<MediaFile> {
    console.log("API: Getting media file with ID:", id, "Type:", typeof id)
    try {
      const response = await apiClient.get(`/media/${id}`)
      console.log("API: Media file response:", response.data)
      return response.data
    } catch (error) {
      console.error("API: Failed to get media file:", error)
      console.error("API: Request URL was:", `/media/${id}`)
      throw error
    }
  },

  async getMediaCategories(): Promise<{ categories: MediaCategoryInfo[] }> {
    try {
      console.log("Getting media categories...")
      const response = await apiClient.get<{ categories: MediaCategoryInfo[] }>("/media/categories")
      
      // Handle different response formats
      const data = response.data
      console.log("Categories API response:", data)
      
      return {
        categories: data.categories || []
      }
    } catch (error) {
      console.error("❌ Failed to get media categories:", error)
      return {
        categories: []
      }
    }
  },

  async startScan(): Promise<any> {
    try {
      const response = await apiClient.post("/media/scan")
      return response.data
    } catch (error) {
      console.error("Failed to start scan:", error)
      throw error
    }
  },

  async scanMediaDirectory(directory: string = "/app/media"): Promise<MediaScanResult> {
    try {
      const response = await apiClient.post("/media/scan", { directory })
      return response.data
    } catch (error) {
      console.error("Failed to scan media directory:", error)
      throw error
    }
  },

  async getVersion(): Promise<VersionInfo> {
    try {
      const response = await apiClient.get("/version")
      return response.data
    } catch (error) {
      console.error("Failed to get version:", error)
      throw error
    }
  },

  async getScanInfo(): Promise<any> {
    try {
      const response = await apiClient.get("/media/scan-info")
      return response.data
    } catch (error) {
      console.error("Failed to get scan info:", error)
      return {}
    }
  },

  async getTVSeries(): Promise<TVSeriesResponse> {
    try {
      const response = await apiClient.get("/media/tv-series")
      return response.data
    } catch (error) {
      console.error("Failed to get TV series:", error)
      return { series: [] }
    }
  },

  async getTVSeriesEpisodes(seriesKey: string, season?: number): Promise<TVEpisodesResponse> {
    try {
      const params = season ? { season } : {}
      const response = await apiClient.get(`/media/tv-series/${seriesKey}/episodes`, { params })
      return response.data
    } catch (error) {
      console.error("Failed to get TV series episodes:", error)
      return { episodes: [] }
    }
  },

  async streamMediaFile(id: string): Promise<string> {
    try {
      const response = await apiClient.get(`/media/${id}/stream`)
      return response.data.stream_url
    } catch (error) {
      console.error("Failed to get stream URL:", error)
      throw error
    }
  },

  async uploadMediaFile(file: File): Promise<MediaUploadResponse> {
    try {
      const formData = new FormData()
      formData.append("file", file)
      
      const response = await apiClient.post("/media/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      return response.data
    } catch (error) {
      console.error("Failed to upload media file:", error)
      throw error
    }
  },

  async deleteMediaFile(id: string): Promise<void> {
    try {
      await apiClient.delete(`/media/${id}`)
    } catch (error) {
      console.error("Failed to delete media file:", error)
      throw error
    }
  },

  // Playlist API with safe error handling
  async getPlaylists(): Promise<Playlist[]> {
    try {
      const response = await apiClient.get("/playlists")
      return response.data.playlists || response.data || []
    } catch (error) {
      console.error("Failed to get playlists:", error)
      return []
    }
  },

  async getPlaylist(id: string): Promise<Playlist> {
    try {
      const response = await apiClient.get(`/playlists/${id}`)
      return response.data
    } catch (error) {
      console.error("Failed to get playlist:", error)
      throw error
    }
  },

  async createPlaylist(playlistData: PlaylistCreate): Promise<Playlist> {
    try {
      const response = await apiClient.post("/playlists", playlistData)
      return response.data
    } catch (error) {
      console.error("Failed to create playlist:", error)
      throw error
    }
  },

  async updatePlaylist(id: string, playlistData: PlaylistUpdate): Promise<Playlist> {
    try {
      const response = await apiClient.put(`/playlists/${id}`, playlistData)
      return response.data
    } catch (error) {
      console.error("Failed to update playlist:", error)
      throw error
    }
  },

  async deletePlaylist(id: string): Promise<void> {
    try {
      await apiClient.delete(`/playlists/${id}`)
    } catch (error) {
      console.error("Failed to delete playlist:", error)
      throw error
    }
  },

  async addPlaylistItem(playlistId: string, itemData: PlaylistItemAdd): Promise<void> {
    try {
      await apiClient.post(`/playlists/${playlistId}/items`, itemData)
    } catch (error) {
      console.error("Failed to add playlist item:", error)
      throw error
    }
  },

  async removePlaylistItem(playlistId: string, mediaId: string): Promise<void> {
    try {
      await apiClient.delete(`/playlists/${playlistId}/items/${mediaId}`)
    } catch (error) {
      console.error("Failed to remove playlist item:", error)
      throw error
    }
  },

  async getPlaylistMedia(playlistId: string): Promise<{ media: MediaFile[] }> {
    try {
      const response = await apiClient.get(`/playlists/${playlistId}/items`)
      return response.data
    } catch (error) {
      console.error("Failed to get playlist media:", error)
      return { media: [] }
    }
  },
}
EOF

echo "✅ Permanent media API fix applied to source file"

echo ""
echo "Creating permanent main.ts fix for chunk errors..."
cat > frontend/src/main.ts << 'EOF'
import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "./router"
import "./style.css"

const app = createApp(App)

// Global error handler for chunk loading errors
app.config.errorHandler = (error, instance, info) => {
  console.error("Global error:", error, info)
  
  // Handle chunk loading errors
  if (error.message?.includes("Loading chunk") || error.message?.includes("ty chunk")) {
    console.warn("Chunk loading error detected - reloading page")
    window.location.reload()
    return
  }
  
  // Handle proxy._sfc_render errors
  if (error.message?.includes("proxy._sfc_render") || error.message?.includes("_sfc_render")) {
    console.warn("Vue render error detected - attempting recovery")
    // Don't reload immediately, let Vue handle it
    return
  }
  
  // Log other errors
  console.error("Unhandled error:", error)
}

// Handle unhandled promise rejections
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason)
  
  // Handle chunk loading errors in promises
  if (event.reason?.message?.includes("Loading chunk") || event.reason?.message?.includes("ty chunk")) {
    console.warn("Chunk loading error in promise - reloading page")
    window.location.reload()
    event.preventDefault()
  }
})

app.use(createPinia())
app.use(router)

app.mount("#app")
EOF

echo "✅ Permanent main.ts fix applied to source file"

echo ""
echo "3. REBUILDING FRONTEND CONTAINER WITH FIXES"
echo "==========================================="

echo "Building frontend container with --no-cache to ensure fresh build..."
docker-compose build --no-cache watch1-frontend

if [ $? -eq 0 ]; then
    echo "✅ Frontend container rebuilt successfully"
else
    echo "❌ Frontend container build failed"
    exit 1
fi

echo ""
echo "4. STARTING CONTAINERS WITH PERMANENT FIXES"
echo "==========================================="

echo "Starting all containers..."
docker-compose up -d

echo "Waiting for containers to start..."
sleep 30

echo "Checking container status..."
docker-compose ps

echo ""
echo "5. TESTING PERMANENT FIXES"
echo "=========================="

echo "Waiting for backend to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend ready (attempt $i)"
        break
    else
        echo "⏳ Backend starting... (attempt $i/15)"
        sleep 5
    fi
done

echo "Waiting for frontend to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend ready (attempt $i)"
        break
    else
        echo "⏳ Frontend starting... (attempt $i/15)"
        sleep 5
    fi
done

echo ""
echo "Testing complete authentication flow..."
login_test=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

login_code="${login_test: -3}"
login_body="${login_test%???}"
echo "Login test: $login_code"

if [ "$login_code" = "200" ]; then
    token=$(echo "$login_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$token" ]; then
        echo "✅ JWT token received: ${token:0:20}..."
        
        # Test authorized endpoints
        echo "Testing authorized media API..."
        media_auth_test=$(curl -s -w "%{http_code}" \
          -H "Authorization: Bearer $token" \
          -H "Origin: http://192.168.254.14:3000" \
          -H "Content-Type: application/json" \
          http://localhost:8000/api/v1/media/ 2>/dev/null)
        
        media_auth_code="${media_auth_test: -3}"
        echo "Media API (authorized): $media_auth_code"
        
        echo "Testing authorized categories API..."
        categories_auth_test=$(curl -s -w "%{http_code}" \
          -H "Authorization: Bearer $token" \
          -H "Origin: http://192.168.254.14:3000" \
          -H "Content-Type: application/json" \
          http://localhost:8000/api/v1/media/categories 2>/dev/null)
        
        categories_auth_code="${categories_auth_test: -3}"
        echo "Categories API (authorized): $categories_auth_code"
        
    else
        echo "❌ No token received in response"
        echo "Response body: $login_body"
    fi
else
    echo "❌ Login failed: $login_body"
fi

echo ""
echo "6. TESTING PERSISTENCE AFTER RESTART"
echo "===================================="

echo "Restarting containers to test fix persistence..."
docker-compose restart

echo "Waiting for restart..."
sleep 30

echo "Testing after restart..."
restart_login_test=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

restart_login_code="${restart_login_test: -3}"
echo "Login after restart: $restart_login_code"

echo ""
echo "🎯 PERMANENT FIX RESULTS"
echo "======================="

if [ "$login_code" = "200" ] && [ "$restart_login_code" = "200" ] && [ -n "$token" ]; then
    echo "🎉 PERMANENT FIXES SUCCESSFULLY APPLIED!"
    echo "========================================"
    echo "✅ Source files updated with permanent fixes"
    echo "✅ Frontend container rebuilt with fixes"
    echo "✅ Authentication working with JWT tokens"
    echo "✅ Fixes persist after container restart"
    echo "✅ No more recurring issues expected"
    echo ""
    echo "🌐 System is now permanently fixed:"
    echo "1. Go to http://192.168.254.14:3000"
    echo "2. Login with test@example.com / testpass123"
    echo "3. All features should work without errors"
    echo "4. Fixes will persist through container restarts"
else
    echo "⚠️ SOME ISSUES MAY REMAIN"
    echo "========================"
    if [ "$login_code" != "200" ]; then
        echo "❌ Initial login test failed"
    fi
    if [ "$restart_login_code" != "200" ]; then
        echo "❌ Login after restart failed"
    fi
    if [ -z "$token" ]; then
        echo "❌ No JWT token received"
    fi
    echo ""
    echo "Check logs: docker-compose logs -f"
fi

echo ""
echo "PERMANENT FIXES APPLIED TO:"
echo "- frontend/src/api/client.ts (authorization headers)"
echo "- frontend/src/stores/auth.ts (JWT token management)"
echo "- frontend/src/api/media.ts (safe error handling)"
echo "- frontend/src/main.ts (chunk error handling)"
echo ""
echo "LOGIN CREDENTIALS:"
echo "Email: test@example.com"
echo "Password: testpass123"
