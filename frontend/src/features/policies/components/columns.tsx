import { ColumnDef } from '@tanstack/react-table'
import { DataTableColumnHeader } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { format, isValid } from 'date-fns'

// Define the Policy type
export interface Policy {
  id: number
  policy_type: string
  policy_number: string
  carrier: string
  annual_premium: number
  effective_date: string | null
  expiration_date: string | null
  is_active: boolean
  business: {
    id: number
    name: string
  }
  documents?: {
    id: number
    name: string
    file: string
    description?: string
  }[]
  created_at: string
  updated_at: string
}

// Helper function to safely format dates
const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  if (!isValid(date)) return 'Invalid date';
  
  return format(date, 'MM/dd/yyyy');
}

export const columns: ColumnDef<Policy>[] = [
  {
    accessorKey: 'policy_type',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Type' />
    ),
    cell: ({ row }) => {
      const policyType = row.getValue('policy_type') as string
      return (
        <Badge variant='outline' className='capitalize'>
          {policyType.replace('_', ' ')}
        </Badge>
      )
    },
  },
  {
    accessorKey: 'business',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Business' />
    ),
    cell: ({ row }) => {
      const business = row.getValue('business') as Policy['business']
      return (
        <span className='font-medium'>
          {business.name}
        </span>
      )
    },
  },
  {
    accessorKey: 'policy_number',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Policy Number' />
    ),
    cell: ({ row }) => (
      <span className='font-medium'>
        {row.getValue('policy_number') || 'N/A'}
      </span>
    ),
  },
  {
    accessorKey: 'carrier',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Carrier' />
    ),
    cell: ({ row }) => (
      <span className='font-medium'>
        {row.getValue('carrier') || 'N/A'}
      </span>
    ),
  },
  {
    accessorKey: 'annual_premium',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Premium' />
    ),
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue('annual_premium') || '0')
      const formatted = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(amount)
      return <span>{formatted}</span>
    },
  },
  {
    accessorKey: 'effective_date',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Effective Date' />
    ),
    cell: ({ row }) => {
      const date = row.getValue('effective_date') as string | null
      return <span>{formatDate(date)}</span>
    },
  },
  {
    accessorKey: 'expiration_date',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Expiration Date' />
    ),
    cell: ({ row }) => {
      const date = row.getValue('expiration_date') as string | null
      return <span>{formatDate(date)}</span>
    },
  },
  {
    accessorKey: 'is_active',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Status' />
    ),
    cell: ({ row }) => {
      const isActive = row.getValue('is_active') as boolean
      return (
        <Badge variant={isActive ? 'default' : 'secondary'}>
          {isActive ? 'Active' : 'Inactive'}
        </Badge>
      )
    },
  },
] 