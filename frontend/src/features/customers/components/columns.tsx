import { ColumnDef } from '@tanstack/react-table'
import { Customer } from '../data/schema'
import { DataTableColumnHeader } from './data-table-column-header'
import { DataTableRowActions } from './data-table-row-actions'
import { Badge } from '@/components/ui/badge'

export const columns: ColumnDef<Customer>[] = [
  {
    accessorKey: 'first_name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='First Name' />
    ),
    cell: ({ row }) => (
      <span className='font-medium'>
        {row.getValue('first_name')}
      </span>
    ),
  },
  {
    accessorKey: 'last_name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Last Name' />
    ),
    cell: ({ row }) => (
      <span className='font-medium'>
        {row.getValue('last_name')}
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
        {row.getValue('email')}
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
        {row.getValue('phone_number')}
      </span>
    ),
  },
  {
    accessorKey: 'businesses',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='Businesses' />
    ),
    cell: ({ row }) => {
      const businesses = row.getValue('businesses') as Customer['businesses']
      return (
        <div className='flex flex-wrap gap-1'>
          {businesses?.map(business => (
            <Badge key={business.id} variant='outline'>
              {business.name}
            </Badge>
          ))}
        </div>
      )
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => <DataTableRowActions row={row} />,
  },
]
