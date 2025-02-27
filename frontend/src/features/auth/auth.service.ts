import { apiClient } from '@/lib/api-client'

interface User {
  id: number
  username: string
  email: string
  is_staff: boolean
}

interface LoginResponse {
  detail: string
}

interface ErrorResponse {
  error: string
}

// Add a cache for the current user
let cachedUser: User | null = null;
let cacheExpiry: number | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

export async function login(username: string, password: string): Promise<LoginResponse> {
  try {
    const response = await apiClient('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
      skipAuth: true, // Skip auth check for login request
    })

    if (!response.ok) {
      const errorData: ErrorResponse = await response.json()
      if (response.status === 401) {
        throw new Error('Invalid username or password')
      }
      throw new Error(errorData.error || 'Login failed')
    }

    // Clear the user cache on login
    cachedUser = null;
    cacheExpiry = null;

    return response.json()
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('Unable to connect to the server')) {
        throw new Error('Unable to connect to the server. Please ensure the server is running and try again.')
      }
      throw error
    }
    throw new Error('An unexpected error occurred during login')
  }
}

export async function logout(): Promise<void> {
  try {
    const response = await apiClient('/api/auth/logout/', {
      method: 'POST',
      skipAuth: true, // Skip auth check for logout request
    })

    if (!response.ok) {
      const errorData: ErrorResponse = await response.json()
      throw new Error(errorData.error || 'Logout failed')
    }

    // Clear the user cache on logout
    cachedUser = null;
    cacheExpiry = null;

    // Clear any stored tokens or session data
    document.cookie.split(';').forEach(cookie => {
      const [name] = cookie.trim().split('=')
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`
    })
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('Unable to connect to the server')) {
        throw new Error('Unable to connect to the server. Please try logging out again.')
      }
      throw error
    }
    throw new Error('An unexpected error occurred during logout')
  }
}

export async function getCurrentUser(): Promise<User> {
  // Check if we have a cached user and the cache hasn't expired
  const now = Date.now();
  if (cachedUser && cacheExpiry && now < cacheExpiry) {
    return cachedUser;
  }

  try {
    const response = await apiClient('/api/auth/user/')

    if (!response.ok) {
      // Clear cache on error
      cachedUser = null;
      cacheExpiry = null;
      throw new Error('Failed to get current user')
    }

    const user = await response.json();
    
    // Cache the user and set expiry
    cachedUser = user;
    cacheExpiry = now + CACHE_DURATION;
    
    return user;
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('Unable to connect to the server')) {
        throw new Error('Unable to connect to the server. Please ensure you are connected to the internet.')
      }
      throw error
    }
    throw new Error('An unexpected error occurred while getting user information')
  }
} 