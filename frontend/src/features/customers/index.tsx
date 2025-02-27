import { useEffect, useState } from 'react'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { columns } from './components/columns'
import { DataTable } from './components/data-table'
import { CustomersDialogs } from './components/customers-dialogs'
import { CustomersPrimaryButtons } from './components/customers-primary-buttons'
import CustomersProvider from './context/customers-context'
import { Customer } from './data/schema'
import { fetchCustomers } from './data/customers'
import { useAuth } from '@/features/auth/context/auth-context'
import { useAgency } from '@/features/auth/context/agency-context'
import { LoadingSpinner } from '@/components/loading-spinner'

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()
  const { selectedAgency } = useAgency()

  useEffect(() => {
    const loadCustomers = async () => {
      if (!selectedAgency) {
        setError('Please select an agency to view customers')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const data = await fetchCustomers(selectedAgency.id)
        setCustomers(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load customers')
        console.error('Error loading customers:', err)
      } finally {
        setLoading(false)
      }
    }

    loadCustomers()
  }, [user, selectedAgency])

  return (
    <CustomersProvider>
      <Header fixed>
        <Search />
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className='mb-2 flex flex-wrap items-center justify-between gap-x-4 space-y-2'>
          <div>
            <h2 className='text-2xl font-bold tracking-tight'>Customers</h2>
            <p className='text-muted-foreground'>
              {selectedAgency ? (
                <>Manage customers for {selectedAgency.name}</>
              ) : (
                'Please select an agency to view customers'
              )}
            </p>
          </div>
          <CustomersPrimaryButtons />
        </div>
        <div className='-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-x-12 lg:space-y-0'>
          {loading ? (
            <div className='flex h-32 items-center justify-center'>
              <LoadingSpinner size='lg' />
            </div>
          ) : error ? (
            <div className='flex h-32 items-center justify-center'>
              <p className='text-red-500'>{error}</p>
            </div>
          ) : (
            <DataTable data={customers} columns={columns} />
          )}
        </div>
      </Main>

      <CustomersDialogs />
    </CustomersProvider>
  )
}
