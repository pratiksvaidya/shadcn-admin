import { ColumnDef } from '@tanstack/react-table'
import { Business } from '../data/schema'
import { DataTableColumnHeader } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'

export const columns: ColumnDef<Business>[] = [
  {
    accessorKey: 'name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Business Name' />
    ),
    cell: ({ row }) => (
      <span className='font-medium'>
        {row.getValue('name')}
      </span>
    ),
  },
  {
    accessorKey: 'email',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Email' />
    ),
    cell: ({ row }) => (
      <span className='text-muted-foreground'>
        {row.getValue('email') || 'N/A'}
      </span>
    ),
  },
  {
    accessorKey: 'phone_number',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Phone' />
    ),
    cell: ({ row }) => (
      <span className='text-muted-foreground'>
        {row.getValue('phone_number') || 'N/A'}
      </span>
    ),
  },
  {
    accessorKey: 'address',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Address' />
    ),
    cell: ({ row }) => (
      <span className='text-muted-foreground'>
        {row.getValue('address') || 'N/A'}
      </span>
    ),
  },
] 