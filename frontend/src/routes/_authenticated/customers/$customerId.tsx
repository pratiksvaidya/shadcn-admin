import { createFileRoute } from '@tanstack/react-router'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { LoadingSpinner } from '@/components/loading-spinner'
import { useAgency } from '@/features/auth/context/agency-context'
import { useEffect, useState } from 'react'
import { Customer } from '@/features/customers/data/schema'
import { fetchCustomers } from '@/features/customers/data/customers'
import { Button } from '@/components/ui/button'
import { IconArrowLeft } from '@tabler/icons-react'
import { useNavigate } from '@tanstack/react-router'

export const Route = createFileRoute('/_authenticated/customers/$customerId')({
  component: CustomerDetail,
})

function CustomerDetail() {
  const { customerId } = Route.useParams()
  const { selectedAgency } = useAgency()
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const loadCustomer = async () => {
      if (!selectedAgency) {
        setError('Please select an agency to view customer details')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const customers = await fetchCustomers(selectedAgency.id)
        const customer = customers.find(c => c.id === parseInt(customerId))
        if (!customer) {
          throw new Error('Customer not found')
        }
        setCustomer(customer)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load customer')
        console.error('Error loading customer:', err)
      } finally {
        setLoading(false)
      }
    }

    loadCustomer()
  }, [customerId, selectedAgency])

  return (
    <>
      <Header fixed>
        <div className='flex items-center gap-2'>
          <Button
            variant='ghost'
            size='sm'
            onClick={() => history.back()}
          >
            <IconArrowLeft className='mr-2 h-4 w-4' />
            Back
          </Button>
          <div>
            <h1 className='text-lg font-semibold'>
              {customer ? `${customer.first_name} ${customer.last_name}` : 'Customer Details'}
            </h1>
            {selectedAgency && (
              <p className='text-sm text-muted-foreground'>
                {customer?.email}
              </p>
            )}
          </div>
        </div>
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        {loading ? (
          <div className='flex h-32 items-center justify-center'>
            <LoadingSpinner size='lg' />
          </div>
        ) : error ? (
          <div className='flex h-32 items-center justify-center'>
            <p className='text-red-500'>{error}</p>
          </div>
        ) : customer ? (
          <div className='space-y-6'>
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              <div className='space-y-2'>
                <h2 className='text-lg font-semibold'>Contact Information</h2>
                <div className='rounded-lg border p-4'>
                  <div className='space-y-2'>
                    <div>
                      <label className='text-sm text-muted-foreground'>Email</label>
                      <p>{customer.email}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Phone</label>
                      <p>{customer.phone_number}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className='space-y-2'>
                <h2 className='text-lg font-semibold'>Businesses</h2>
                <div className='rounded-lg border p-4'>
                  {customer.businesses && customer.businesses.length > 0 ? (
                    <div className='space-y-4'>
                      {customer.businesses.map(business => (
                        <div key={business.id} className='space-y-2'>
                          <p className='font-medium'>{business.name}</p>
                          {business.description && (
                            <p className='text-sm text-muted-foreground'>{business.description}</p>
                          )}
                          <Button 
                            variant='outline' 
                            size='sm'
                            onClick={() => navigate({ 
                              to: '/businesses/$businessId', 
                              params: { businessId: business.id.toString() } 
                            })}
                          >
                            View Business Details
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className='text-sm text-muted-foreground'>No businesses yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className='flex h-32 items-center justify-center'>
            <p className='text-muted-foreground'>Customer not found</p>
          </div>
        )}
      </Main>
    </>
  )
} 