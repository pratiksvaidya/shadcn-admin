import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { getCurrentUser, login as loginApi, logout as logoutApi } from '../auth.service'
import { useToast } from '@/hooks/use-toast'

interface User {
  id: number
  username: string
  email: string
  is_staff: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    const initAuth = async () => {
      try {
        const user = await getCurrentUser()
        setUser(user)
        // If we're on the sign-in page and already authenticated, redirect to home
        if (window.location.pathname === '/sign-in') {
          navigate({ to: '/' })
        }
      } catch (error) {
        // Don't show error on initial load if not logged in
        if (!(error instanceof Error && error.message.includes('login to continue'))) {
          setError(error instanceof Error ? error.message : 'Failed to get user')
        }
        // If we're not on the sign-in page and not authenticated, redirect to sign-in
        if (window.location.pathname !== '/sign-in') {
          navigate({ 
            to: '/sign-in',
            search: { redirect: window.location.pathname }
          })
        }
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [navigate])

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true)
      setError(null)
      await loginApi(username, password)
      const user = await getCurrentUser()
      setUser(user)
      toast({
        title: 'Success',
        description: 'You have been logged in successfully.',
      })
      // Get redirect URL from search params
      const params = new URLSearchParams(window.location.search)
      const redirectTo = params.get('redirect') || '/'
      navigate({ to: redirectTo })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to login'
      setError(message)
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      })
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      setIsLoading(true)
      setError(null)
      await logoutApi()
      setUser(null)
      toast({
        title: 'Success',
        description: 'You have been logged out successfully.',
      })
      // Always redirect to sign-in after logout, regardless of any errors
      navigate({ to: '/sign-in' })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to logout'
      setError(message)
      toast({
        title: 'Warning',
        description: 'Session ended. Please sign in again.',
        variant: 'default',
      })
      // Clear user state and redirect to sign-in even if logout API fails
      setUser(null)
      navigate({ to: '/sign-in' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        error,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 