import { useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { columns } from './components/columns'
import { DataTable } from '@/components/ui/data-table'
import { CustomersDialogs } from './components/customers-dialogs'
import { CustomersPrimaryButtons } from './components/customers-primary-buttons'
import CustomersProvider from './context/customers-context'
import { Customer } from './data/schema'
import { fetchCustomers } from './data/customers'
import { useAuth } from '@/features/auth/context/auth-context'
import { useAgency } from '@/features/auth/context/agency-context'
import { DataTableRowActions } from '@/components/ui/data-table'
import { useCustomers } from './context/customers-context'
import { IconTrash } from '@tabler/icons-react'
import { Row, FilterFn } from '@tanstack/react-table'

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()
  const { selectedAgency } = useAgency()
  const navigate = useNavigate()

  useEffect(() => {
    async function getCustomers() {
      if (!user || !selectedAgency) {
        setLoading(false)
        return
      }

      setLoading(true)
      setError(null)

      try {
        const data = await fetchCustomers(selectedAgency.id)
        setCustomers(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch customers')
      } finally {
        setLoading(false)
      }
    }

    getCustomers()
  }, [user, selectedAgency])

  const handleRowClick = (row: Row<Customer>) => {
    const customer = row.original
    navigate({
      to: '/customers/$customerId',
      params: { customerId: customer.id.toString() }
    })
  }

  // Custom global filter function for customers
  const customersGlobalFilter: FilterFn<Customer> = (row, columnId, filterValue) => {
    const searchValue = filterValue.toLowerCase()
    const customer = row.original

    // Search in basic fields
    const basicFields = [
      customer.first_name,
      customer.last_name,
      customer.email,
      customer.phone_number,
    ]
    if (basicFields.some(field => field?.toLowerCase().includes(searchValue))) {
      return true
    }

    // Search in business names
    if (customer.businesses?.some(business => 
      business.name?.toLowerCase().includes(searchValue)
    )) {
      return true
    }

    return false
  }

  // Custom row actions component for customers
  const CustomerRowActions = ({ row }: { row: Row<Customer> }) => {
    const customer = row.original
    const { setOpen, setCurrentRow } = useCustomers()

    const actions = [
      {
        label: 'Edit',
        onClick: () => {
          setCurrentRow(customer)
          setOpen('update')
        }
      },
      {
        label: 'Add Business',
        onClick: () => {
          setCurrentRow(customer)
          setOpen('create')
        }
      },
      {
        label: 'Delete',
        onClick: () => {
          setCurrentRow(customer)
          setOpen('delete')
        },
        className: 'text-red-600',
        icon: <IconTrash size={16} />,
        separator: true
      }
    ]

    return <DataTableRowActions row={row} actions={actions} />
  }

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
          <DataTable 
            data={customers} 
            columns={columns} 
            onRowClick={handleRowClick}
            rowActions={CustomerRowActions}
            searchPlaceholder="Search customers..."
            globalFilterFn={customersGlobalFilter}
            isLoading={loading}
            error={error}
            emptyMessage={selectedAgency ? "No customers found." : "Please select an agency to view customers."}
          />
        </div>
      </Main>

      <CustomersDialogs />
    </CustomersProvider>
  )
}
