import { apiClient } from '@/lib/api-client'
import { Customer, customerSchema } from './schema'

export async function fetchCustomers(agencyId: number): Promise<Customer[]> {
  if (!agencyId) {
    throw new Error('Please select an agency to view customers')
  }

  const response = await apiClient(`/api/customers/?agency_id=${agencyId}`)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to view customers')
    }
    throw new Error('Failed to fetch customers')
  }

  const data = await response.json()
  return data.map((customer: unknown) => customerSchema.parse(customer))
}

export async function createCustomer(
  customer: Omit<Customer, 'id' | 'created_at' | 'updated_at' | 'businesses'>,
  agencyId: number
): Promise<Customer> {
  if (!agencyId) {
    throw new Error('Please select an agency to create customers')
  }

  const response = await apiClient('/api/customers/', {
    method: 'POST',
    body: JSON.stringify({
      ...customer,
      agency_id: agencyId
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to create customers')
    }
    const error = await response.json()
    throw new Error(error.error || 'Failed to create customer')
  }

  const data = await response.json()
  return customerSchema.parse(data)
}

export async function updateCustomer(
  id: number,
  customer: Partial<Omit<Customer, 'id' | 'created_at' | 'updated_at' | 'businesses'>>,
  agencyId: number
): Promise<Customer> {
  if (!agencyId) {
    throw new Error('Please select an agency to update customers')
  }

  const response = await apiClient(`/api/customers/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify({
      ...customer,
      agency_id: agencyId
    }),
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to update customers')
    }
    const error = await response.json()
    throw new Error(error.error || 'Failed to update customer')
  }

  const data = await response.json()
  return customerSchema.parse(data)
}

export async function deleteCustomer(id: number, agencyId: number): Promise<void> {
  if (!agencyId) {
    throw new Error('Please select an agency to delete customers')
  }

  const response = await apiClient(`/api/customers/${id}/?agency_id=${agencyId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please login to delete customers')
    }
    throw new Error('Failed to delete customer')
  }
} 