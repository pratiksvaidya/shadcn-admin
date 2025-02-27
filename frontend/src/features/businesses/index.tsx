import { useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { columns } from './components/columns'
import { DataTable, DataTableRowActions } from '@/components/ui/data-table'
import { useAuth } from '@/features/auth/context/auth-context'
import { useAgency } from '@/features/auth/context/agency-context'
import { IconTrash, IconEdit, IconEye } from '@tabler/icons-react'
import { Row, FilterFn } from '@tanstack/react-table'
import { Button } from '@/components/ui/button'
import { fetchBusinesses, deleteBusiness } from './data/api'
import { Business } from './data/schema'
import { toast } from '@/hooks/use-toast'

export default function Businesses() {
  const [businesses, setBusinesses] = useState<Business[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()
  const { selectedAgency } = useAgency()
  const navigate = useNavigate()

  useEffect(() => {
    async function loadBusinesses() {
      if (!selectedAgency) return

      setLoading(true)
      setError(null)

      try {
        const data = await fetchBusinesses(selectedAgency.id)
        setBusinesses(data)
      } catch (err) {
        console.error('Error loading businesses:', err)
        setError(err instanceof Error ? err.message : 'Failed to load businesses')
        toast({
          title: 'Error',
          description: err instanceof Error ? err.message : 'Failed to load businesses',
          variant: 'destructive',
        })
      } finally {
        setLoading(false)
      }
    }

    loadBusinesses()
  }, [selectedAgency])

  const handleRowClick = (row: Row<Business>) => {
    navigate({
      to: '/businesses/$businessId',
      params: { businessId: row.original.id.toString() }
    })
  }

  const handleDeleteBusiness = async (id: number) => {
    if (!selectedAgency) return

    try {
      await deleteBusiness(id, selectedAgency.id)
      setBusinesses(businesses.filter(business => business.id !== id))
      toast({
        title: 'Success',
        description: 'Business deleted successfully',
      })
    } catch (err) {
      console.error('Error deleting business:', err)
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete business',
        variant: 'destructive',
      })
    }
  }

  // Custom global filter function for businesses
  const businessesGlobalFilter: FilterFn<Business> = (row, columnId, filterValue) => {
    const searchValue = filterValue.toLowerCase()
    const business = row.original

    // Search in basic fields
    const basicFields = [
      business.name,
      business.email,
      business.phone_number,
      business.address,
      business.description,
    ]
    
    return basicFields.some(field => field?.toLowerCase().includes(searchValue))
  }

  // Custom row actions component for businesses
  const BusinessRowActions = ({ row }: { row: Row<Business> }) => {
    const business = row.original

    const actions = [
      {
        label: 'View Details',
        onClick: () => {
          navigate({
            to: '/businesses/$businessId',
            params: { businessId: business.id.toString() }
          })
        },
        icon: <IconEye size={16} />
      },
      {
        label: 'Edit',
        onClick: () => {
          navigate({
            to: '/businesses/$businessId',
            params: { businessId: business.id.toString() }
          })
        },
        icon: <IconEdit size={16} />
      },
      {
        label: 'Delete',
        onClick: () => {
          if (window.confirm(`Are you sure you want to delete business ${business.name}?`)) {
            handleDeleteBusiness(business.id)
          }
        },
        className: 'text-red-600',
        icon: <IconTrash size={16} />,
        separator: true
      }
    ]

    return <DataTableRowActions row={row} actions={actions} />
  }

  return (
    <>
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
            <h2 className='text-2xl font-bold tracking-tight'>Businesses</h2>
            <p className='text-muted-foreground'>
              {selectedAgency ? (
                <>Manage businesses for {selectedAgency.name}</>
              ) : (
                'Please select an agency to view businesses'
              )}
            </p>
          </div>
          <Button onClick={() => navigate({ to: '/businesses' })}>Add Business</Button>
        </div>
        <div className='-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-x-12 lg:space-y-0'>
          <DataTable 
            data={businesses} 
            columns={columns} 
            onRowClick={handleRowClick}
            rowActions={BusinessRowActions}
            searchPlaceholder="Search businesses..."
            globalFilterFn={businessesGlobalFilter}
            isLoading={loading}
            error={error}
            emptyMessage={selectedAgency ? "No businesses found." : "Please select an agency to view businesses."}
          />
        </div>
      </Main>
    </>
  )
} 