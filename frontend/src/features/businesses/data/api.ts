import { apiClient } from '@/lib/api-client'
import { Business, businessSchema } from './schema'
import { Policy, policySchema } from '@/features/policies/data/schema'
import { Document } from './types'

export async function fetchBusinesses(agencyId: number): Promise<Business[]> {
  if (!agencyId) {
    throw new Error('Please select an agency to view businesses')
  }

  const response = await apiClient(`/api/businesses/?agency_id=${agencyId}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to view businesses')
    }
    throw new Error('Failed to fetch businesses')
  }

  const data = await response.json()
  return data.map((business: unknown) => businessSchema.parse(business))
}

export async function fetchBusiness(agencyId: number, businessId: number): Promise<Business | null> {
  if (!agencyId) {
    throw new Error('Please select an agency to view business details')
  }

  const response = await apiClient(`/api/businesses/${businessId}/?agency_id=${agencyId}`)

  if (!response.ok) {
    if (response.status === 404) {
      return null
    }
    if (response.status === 401) {
      throw new Error('Please login to view business details')
    }
    throw new Error('Failed to fetch business details')
  }

  const data = await response.json()
  return businessSchema.parse(data)
}

export async function fetchBusinessPolicies(agencyId: number, businessId: number): Promise<Policy[]> {
  if (!agencyId) {
    throw new Error('Please select an agency to view business policies')
  }

  const response = await apiClient(`/api/policies/?agency_id=${agencyId}&business=${businessId}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to view business policies')
    }
    throw new Error('Failed to fetch business policies')
  }

  const data = await response.json()
  return data.map((policy: unknown) => policySchema.parse(policy))
}

export async function fetchBusinessDocuments(agencyId: number, businessId: number): Promise<Document[]> {
  if (!agencyId) {
    throw new Error('Please select an agency to view business documents')
  }

  const response = await apiClient(`/api/businesses/${businessId}/uploaded_documents/?agency_id=${agencyId}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to view business documents')
    }
    throw new Error('Failed to fetch business documents')
  }

  const data = await response.json()
  return data
}

export async function createBusiness(
  business: Omit<Business, 'id' | 'created_at' | 'updated_at'>,
  agencyId: number
): Promise<Business> {
  if (!agencyId) {
    throw new Error('Please select an agency to create businesses')
  }

  const response = await apiClient('/api/businesses/', {
    method: 'POST',
    body: JSON.stringify({
      ...business,
      agency_id: agencyId
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to create businesses')
    }
    const error = await response.json()
    throw new Error(error.error || 'Failed to create business')
  }

  const data = await response.json()
  return businessSchema.parse(data)
}

export async function updateBusiness(
  id: number,
  business: Partial<Omit<Business, 'id' | 'created_at' | 'updated_at'>>,
  agencyId: number
): Promise<Business> {
  if (!agencyId) {
    throw new Error('Please select an agency to update businesses')
  }

  const response = await apiClient(`/api/businesses/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({
      ...business,
      agency_id: agencyId
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to update businesses')
    }
    const error = await response.json()
    throw new Error(error.error || 'Failed to update business')
  }

  const data = await response.json()
  return businessSchema.parse(data)
}

export async function deleteBusiness(id: number, agencyId: number): Promise<void> {
  if (!agencyId) {
    throw new Error('Please select an agency to delete businesses')
  }

  const response = await apiClient(`/api/businesses/${id}/?agency_id=${agencyId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to delete businesses')
    }
    throw new Error('Failed to delete business')
  }
} 