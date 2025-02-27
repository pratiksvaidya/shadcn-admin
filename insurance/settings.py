CSRF_TRUSTED_ORIGINS = [
    'https://pratik-frontend.ngrok.app',
    'https://pratik-backend.ngrok.app',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:8000',
]

# Modified for Safari compatibility
CSRF_COOKIE_SECURE = False  # Set to False for local development
CSRF_COOKIE_SAMESITE = 'Lax'  # Changed from 'None' to 'Lax' for better Safari compatibility
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access to CSRF token

# Modified for Safari compatibility
SESSION_COOKIE_SECURE = False  # Set to False for local development
SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from 'None' to 'Lax' 