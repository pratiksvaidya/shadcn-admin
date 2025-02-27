import { useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { columns, Policy } from './components/columns'
import { DataTable, DataTableRowActions } from '@/components/ui/data-table'
import { useAuth } from '@/features/auth/context/auth-context'
import { useAgency } from '@/features/auth/context/agency-context'
import { IconTrash, IconEdit, IconEye } from '@tabler/icons-react'
import { Row, FilterFn } from '@tanstack/react-table'
import { Button } from '@/components/ui/button'
import { fetchPolicies, deletePolicy } from './data/api'
import { toast } from '@/hooks/use-toast'

export default function Policies() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()
  const { selectedAgency } = useAgency()
  const navigate = useNavigate()

  const loadPolicies = async () => {
    if (!user || !selectedAgency) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    try {
      const data = await fetchPolicies(selectedAgency.id)
      setPolicies(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch policies')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPolicies()
  }, [user, selectedAgency])

  const handleRowClick = (row: Row<Policy>) => {
    const policy = row.original
    navigate({
      to: '/policies/$policyId',
      params: { policyId: policy.id.toString() }
    })
  }

  const handleDeletePolicy = async (policyId: number) => {
    if (!selectedAgency) return

    try {
      await deletePolicy(policyId, selectedAgency.id)
      toast({
        title: "Success",
        description: "Policy deleted successfully",
        variant: "default",
      })
      // Reload policies after deletion
      loadPolicies()
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to delete policy',
        variant: "destructive",
      })
    }
  }

  // Custom global filter function for policies
  const policiesGlobalFilter: FilterFn<Policy> = (row, columnId, filterValue) => {
    const searchValue = filterValue.toLowerCase()
    const policy = row.original

    // Search in basic fields
    const basicFields = [
      policy.policy_type,
      policy.policy_number,
      policy.carrier,
      policy.business.name,
    ]
    if (basicFields.some(field => field?.toLowerCase().includes(searchValue))) {
      return true
    }

    // Search in premium (convert to string first)
    if (policy.annual_premium.toString().includes(searchValue)) {
      return true
    }

    return false
  }

  // Custom row actions component for policies
  const PolicyRowActions = ({ row }: { row: Row<Policy> }) => {
    const policy = row.original

    const actions = [
      {
        label: 'View Details',
        onClick: () => {
          navigate({
            to: '/policies/$policyId',
            params: { policyId: policy.id.toString() }
          })
        },
        icon: <IconEye size={16} />
      },
      {
        label: 'Edit',
        onClick: () => {
          navigate({
            to: '/policies/$policyId',
            params: { policyId: policy.id.toString() }
          })
        },
        icon: <IconEdit size={16} />
      },
      {
        label: 'Delete',
        onClick: () => {
          if (window.confirm(`Are you sure you want to delete policy ${policy.policy_number || policy.id}?`)) {
            handleDeletePolicy(policy.id)
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
            <h2 className='text-2xl font-bold tracking-tight'>Policies</h2>
            <p className='text-muted-foreground'>
              {selectedAgency ? (
                <>Manage policies for {selectedAgency.name}</>
              ) : (
                'Please select an agency to view policies'
              )}
            </p>
          </div>
          <Button onClick={() => navigate({ to: '/policies' })}>Add Policy</Button>
        </div>
        <div className='-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-x-12 lg:space-y-0'>
          <DataTable 
            data={policies} 
            columns={columns} 
            onRowClick={handleRowClick}
            rowActions={PolicyRowActions}
            searchPlaceholder="Search policies..."
            globalFilterFn={policiesGlobalFilter}
            isLoading={loading}
            error={error}
            emptyMessage={selectedAgency ? "No policies found." : "Please select an agency to view policies."}
          />
        </div>
      </Main>
    </>
  )
} 