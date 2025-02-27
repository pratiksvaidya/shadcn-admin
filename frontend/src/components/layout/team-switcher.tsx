import * as React from 'react'
import { ChevronsUpDown, Building2 } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar'
import { useAgency } from '@/features/auth/context/agency-context'
import { LoadingSpinner } from '@/components/loading-spinner'

export function TeamSwitcher() {
  const { agencies, selectedAgency, isLoading, selectAgency } = useAgency()
  const { isMobile } = useSidebar()

  if (isLoading) {
    return (
      <div className='flex items-center gap-2'>
        <LoadingSpinner size='sm' />
        <span className='text-sm'>Loading agencies...</span>
      </div>
    )
  }

  if (!selectedAgency) {
    return null
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size='lg'
              className='data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground'
            >
              <div className='flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground'>
                <Building2 className='size-4' />
              </div>
              <div className='grid flex-1 text-left text-sm leading-tight'>
                <span className='truncate font-semibold'>
                  {selectedAgency.name}
                </span>
                <span className='truncate text-xs'>{selectedAgency.role}</span>
              </div>
              <ChevronsUpDown className='ml-auto' />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className='w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg'
            align='start'
            side={isMobile ? 'bottom' : 'right'}
            sideOffset={4}
          >
            <DropdownMenuLabel className='text-xs text-muted-foreground'>
              Agencies
            </DropdownMenuLabel>
            {agencies.map((agency) => (
              <DropdownMenuItem
                key={agency.id}
                onClick={() => selectAgency(agency)}
                className='gap-2 p-2'
              >
                <div className='flex size-6 items-center justify-center rounded-sm border'>
                  <Building2 className='size-4 shrink-0' />
                </div>
                {agency.name}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}