import { apiClient } from '@/lib/api-client'
import { Policy } from '../components/columns'
import { z } from 'zod'

// Define a schema for policy data validation
export const policySchema = z.object({
  id: z.number(),
  business: z.number(),
  business_name: z.string(),
  policy_number: z.string().nullable(),
  effective_date: z.string().nullable(),
  expiration_date: z.string().nullable(),
  carrier: z.string().nullable(),
  annual_premium: z.number().nullable(),
  policy_type: z.string(),
  policy_type_display: z.string(),
  is_active: z.boolean(),
  documents: z.array(z.object({
    id: z.number(),
    name: z.string(),
    file: z.string(),
    // Add other document fields as needed
  })).optional(),
  created_at: z.string(),
  updated_at: z.string(),
})

// Type for API response
export type PolicyApiResponse = z.infer<typeof policySchema>

// Convert API response to Policy type
const mapApiResponseToPolicy = (data: PolicyApiResponse): Policy => {
  return {
    id: data.id,
    policy_type: data.policy_type,
    policy_number: data.policy_number || '',
    carrier: data.carrier || '',
    annual_premium: data.annual_premium || 0,
    effective_date: data.effective_date || '',
    expiration_date: data.expiration_date || '',
    is_active: data.is_active,
    business: {
      id: data.business,
      name: data.business_name
    },
    documents: data.documents,
    created_at: data.created_at,
    updated_at: data.updated_at
  }
}

export async function fetchPolicies(agencyId: number): Promise<Policy[]> {
  if (!agencyId) {
    throw new Error('Please select an agency to view policies')
  }

  const response = await apiClient(`/api/policies/?agency_id=${agencyId}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to view policies')
    }
    throw new Error('Failed to fetch policies')
  }

  const data = await response.json()
  return data.map((policy: unknown) => {
    const validatedPolicy = policySchema.parse(policy)
    return mapApiResponseToPolicy(validatedPolicy)
  })
}

export async function fetchPolicy(agencyId: number, policyId: number): Promise<Policy | null> {
  if (!agencyId) {
    throw new Error('Please select an agency to view policy details')
  }

  const response = await apiClient(`/api/policies/${policyId}/?agency_id=${agencyId}`)

  if (!response.ok) {
    if (response.status === 404) {
      return null
    }
    if (response.status === 401) {
      throw new Error('Please login to view policy details')
    }
    throw new Error('Failed to fetch policy details')
  }

  const data = await response.json()
  const validatedPolicy = policySchema.parse(data)
  return mapApiResponseToPolicy(validatedPolicy)
}

export async function createPolicy(
  policy: Omit<Policy, 'id' | 'created_at' | 'updated_at' | 'is_active'>,
  agencyId: number
): Promise<Policy> {
  if (!agencyId) {
    throw new Error('Please select an agency to create policies')
  }

  const response = await apiClient('/api/policies/', {
    method: 'POST',
    body: JSON.stringify({
      ...policy,
      business: policy.business.id,
      agency_id: agencyId
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to create policies')
    }
    const error = await response.json()
    throw new Error(error.error || 'Failed to create policy')
  }

  const data = await response.json()
  const validatedPolicy = policySchema.parse(data)
  return mapApiResponseToPolicy(validatedPolicy)
}

export async function updatePolicy(
  id: number,
  policy: Partial<Omit<Policy, 'id' | 'created_at' | 'updated_at' | 'is_active'>>,
  agencyId: number
): Promise<Policy> {
  if (!agencyId) {
    throw new Error('Please select an agency to update policies')
  }

  // Convert business object to just the ID if it exists
  const policyData = { ...policy }
  if (policyData.business) {
    policyData.business = { id: policyData.business.id } as any
  }

  const response = await apiClient(`/api/policies/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({
      ...policyData,
      business: policyData.business ? (policyData.business as any).id : undefined,
      agency_id: agencyId
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to update policies')
    }
    const error = await response.json()
    throw new Error(error.error || 'Failed to update policy')
  }

  const data = await response.json()
  const validatedPolicy = policySchema.parse(data)
  return mapApiResponseToPolicy(validatedPolicy)
}

export async function deletePolicy(id: number, agencyId: number): Promise<void> {
  if (!agencyId) {
    throw new Error('Please select an agency to delete policies')
  }

  const response = await apiClient(`/api/policies/${id}/?agency_id=${agencyId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to delete policies')
    }
    throw new Error('Failed to delete policy')
  }
}

export async function uploadPolicyDocument(
  policyId: number,
  agencyId: number,
  file: File,
  name?: string,
  description?: string
): Promise<any> {
  if (!agencyId) {
    throw new Error('Please select an agency to upload documents')
  }

  // Create FormData
  const formData = new FormData()
  formData.append('file', file)
  
  if (name) {
    formData.append('name', name)
  }
  
  if (description) {
    formData.append('description', description)
  }

  try {
    console.log(`Uploading document to policy ${policyId} with agency ${agencyId}`)
    
    // Use direct fetch instead of apiClient to avoid Content-Type issues
    const BASE_URL = 'http://localhost:8000'
    const url = `${BASE_URL}/api/policies/${policyId}/add_document/?agency_id=${agencyId}`
    
    // Get CSRF token from cookie
    const getCsrfToken = () => {
      const cookies = document.cookie.split(';')
      for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'csrftoken' && value) {
          return value
        }
      }
      return ''
    }
    
    const csrfToken = getCsrfToken()
    
    // Create headers without Content-Type (browser will set it for FormData)
    const headers: Record<string, string> = {}
    
    // Add CSRF token if available
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
    
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      headers,
      credentials: 'include',
      mode: 'cors'
    })

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Please login to upload documents')
      }
      
      if (response.status === 404) {
        throw new Error('Upload endpoint not found. The URL should be /api/policies/{policyId}/add_document/')
      }
      
      if (response.status === 415) {
        throw new Error('Unsupported media type. The server does not accept the content type of the request.')
      }
      
      // Try to get error details
      let errorMessage = 'Failed to upload document';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.error || errorMessage;
      } catch (e) {
        // If we can't parse the error as JSON, use the status text
        errorMessage = `Upload failed: ${response.statusText}`;
      }
      
      throw new Error(errorMessage);
    }

    return response.json();
  } catch (error) {
    console.error('Document upload error:', error);
    throw error;
  }
}

export async function removePolicyDocument(
  policyId: number,
  documentId: number,
  agencyId: number
): Promise<void> {
  if (!agencyId) {
    throw new Error('Please select an agency to remove documents')
  }

  const response = await apiClient(`/api/policies/${policyId}/remove_document/?agency_id=${agencyId}`, {
    method: 'POST',
    body: JSON.stringify({ document_id: documentId }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to remove documents')
    }
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || 'Failed to remove document')
  }
}

// Define the type for renewal comparison response
export interface RenewalComparison {  
  ai_provider?: 'anthropic' | 'openai'; // The AI provider used for generation
  email?: string; // The email body content from the AI response
  attachment?: string; // The attachment content from the AI response
}

export async function generateRenewalComparison(
  policyId: number,
  agencyId: number,
  aiProvider: 'anthropic' | 'openai' = 'openai'
): Promise<RenewalComparison> {
  if (!agencyId) {
    throw new Error('Please select an agency to generate renewal comparison')
  }

  const response = await apiClient(`/api/policies/${policyId}/generate_renewal_comparison/?agency_id=${agencyId}&ai_provider=${aiProvider}`, {
    method: 'POST',
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to generate renewal comparison')
    }
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || 'Failed to generate renewal comparison')
  }

  return response.json()
} 