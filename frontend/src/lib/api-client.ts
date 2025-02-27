const BASE_URL = 'http://localhost:8000'

let csrfToken: string | null = null

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken

  try {
    const response = await fetch(`${BASE_URL}/api/csrf/`, {
      credentials: 'include',
      mode: 'cors',  // Explicitly set CORS mode
      headers: {
        'Accept': 'application/json',
      },
    })

    if (!response.ok) {
      console.error('CSRF Response not OK:', {
        status: response.status,
        statusText: response.statusText,
      })
      throw new Error(`Failed to get CSRF token: ${response.statusText}`)
    }

    // First try to get the token from the response header
    const headerToken = response.headers.get('X-CSRFToken')
    if (headerToken) {
      csrfToken = headerToken
      return headerToken
    }

    // If no header, try to get from cookies
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'csrftoken' && value) {
        csrfToken = value
        return value
      }
    }

    // Try to get token from response body as fallback
    const data = await response.json()
    if (data.csrfToken) {
      csrfToken = data.csrfToken
      return data.csrfToken
    }

    console.error('No CSRF token found:', {
      cookies: document.cookie,
      responseHeaders: Array.from(response.headers.entries()),
      responseBody: data,
    })
    throw new Error('CSRF token not found in response')
  } catch (error) {
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      console.error('Connection error - Is the Django server running?', {
        url: `${BASE_URL}/api/csrf/`,
        error,
      })
      throw new Error('Unable to connect to the server. Please ensure the Django server is running.')
    }
    console.error('Error getting CSRF token:', error)
    throw error
  }
}

interface RequestOptions extends RequestInit {
  skipAuth?: boolean
}

export async function apiClient(endpoint: string, options: RequestOptions = {}) {
  const { skipAuth = false, ...fetchOptions } = options

  // Always include credentials for cookies
  fetchOptions.credentials = 'include'
  fetchOptions.mode = 'cors'  // Explicitly set CORS mode

  // Set default headers
  fetchOptions.headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  }

  try {
    // Add CSRF token for non-GET requests
    if (fetchOptions.method && fetchOptions.method !== 'GET') {
      const token = await getCsrfToken()
      ;(fetchOptions.headers as Record<string, string>)['X-CSRFToken'] = token
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, fetchOptions)

    // Handle 401 Unauthorized
    if (response.status === 401 && !skipAuth) {
      // Clear CSRF token on unauthorized
      csrfToken = null
      // Redirect to login page
      window.location.href = '/sign-in'
      throw new Error('Please login to continue')
    }

    return response
  } catch (error) {
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      console.error('Connection error - Is the Django server running?', {
        url: `${BASE_URL}${endpoint}`,
        options: fetchOptions,
        error,
      })
      throw new Error('Unable to connect to the server. Please ensure the Django server is running.')
    }
    console.error('API Client Error:', {
      endpoint,
      options: fetchOptions,
      error,
    })
    throw error
  }
}

// Export the base URL for use in other parts of the app
export { BASE_URL } 