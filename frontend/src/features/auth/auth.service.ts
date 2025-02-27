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
  try {
    const response = await apiClient('/api/auth/user/')

    if (!response.ok) {
      throw new Error('Failed to get current user')
    }

    return response.json()
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