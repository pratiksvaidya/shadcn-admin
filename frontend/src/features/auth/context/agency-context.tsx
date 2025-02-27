import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

interface Agency {
  id: number
  name: string
  description: string
  email: string
  phone_number: string
  website: string
  is_active: boolean
  role: string
  is_primary: boolean
  created_at: string
  updated_at: string
}

interface AgencyContextType {
  agencies: Agency[]
  selectedAgency: Agency | null
  isLoading: boolean
  error: string | null
  selectAgency: (agency: Agency) => void
  refreshAgencies: () => Promise<void>
}

const AgencyContext = createContext<AgencyContextType | null>(null)

interface AgencyProviderProps {
  children: React.ReactNode
}

export function AgencyProvider({ children }: AgencyProviderProps) {
  const [agencies, setAgencies] = useState<Agency[]>([])
  const [selectedAgency, setSelectedAgency] = useState<Agency | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  const fetchAgencies = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await apiClient('/api/agencies/')
      
      if (!response.ok) {
        throw new Error('Failed to fetch agencies')
      }

      const data = await response.json()
      setAgencies(data)

      // If there's no selected agency yet, select the first one
      if (!selectedAgency && data.length > 0) {
        setSelectedAgency(data[0])
      }

      // Store the selected agency ID in localStorage
      if (selectedAgency) {
        localStorage.setItem('selectedAgencyId', selectedAgency.id.toString())
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch agencies'
      setError(message)
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    // Try to restore the selected agency from localStorage
    const storedAgencyId = localStorage.getItem('selectedAgencyId')
    if (storedAgencyId) {
      const agency = agencies.find(a => a.id.toString() === storedAgencyId)
      if (agency) {
        setSelectedAgency(agency)
      }
    }
  }, [agencies])

  useEffect(() => {
    fetchAgencies()
  }, [])

  const selectAgency = (agency: Agency) => {
    setSelectedAgency(agency)
    localStorage.setItem('selectedAgencyId', agency.id.toString())
  }

  return (
    <AgencyContext.Provider
      value={{
        agencies,
        selectedAgency,
        isLoading,
        error,
        selectAgency,
        refreshAgencies: fetchAgencies,
      }}
    >
      {children}
    </AgencyContext.Provider>
  )
}

export function useAgency() {
  const context = useContext(AgencyContext)
  if (!context) {
    throw new Error('useAgency must be used within an AgencyProvider')
  }
  return context
} 