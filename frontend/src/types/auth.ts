export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser?: boolean
  avatar_url?: string
  created_at: string
  updated_at?: string
  last_login?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface TokenData {
  user_id: string
}

export interface ColorPalette {
  primary: string
  secondary: string
  accent: string
  background: string
  surface: string
  text: string
  text_secondary: string
  border: string
  success: string
  warning: string
  error: string
}

export interface UserPreferences {
  user_id: string
  color_palette: ColorPalette
  theme: string
  layout: string
  items_per_page: number
  auto_scan: boolean
  show_thumbnails: boolean
  created_at: string
  updated_at: string
}

export interface UserPreferencesUpdate {
  color_palette?: ColorPalette
  theme?: string
  layout?: string
  items_per_page?: number
  auto_scan?: boolean
  show_thumbnails?: boolean
}
