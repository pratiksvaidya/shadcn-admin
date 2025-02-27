import {
  IconPackages,
  IconPalette,
  IconSettings,
  IconUsers,
  IconFileText,
  IconBuildingStore,
} from '@tabler/icons-react'
import { GalleryVerticalEnd } from 'lucide-react'
import { type SidebarData } from '../types'

export const sidebarData: Omit<SidebarData, 'user'> = {
  teams: [
    {
      name: "Insurance Agency",
      logo: GalleryVerticalEnd,
      plan: 'Premium',
    },
  ],
  navGroups: [
    {
      title: 'General',
      items: [
        {
          title: 'Customers',
          url: '/',
          icon: IconUsers,
        },
        {
          title: 'Businesses',
          url: '/businesses',
          icon: IconBuildingStore,
        },
        {
          title: 'Policies',
          url: '/policies',
          icon: IconFileText,
        },
        {
          title: 'Apps',
          url: '/apps',
          icon: IconPackages,
        },
      ],
    },
    {
      title: 'Other',
      items: [
        {
          title: 'Settings',
          icon: IconSettings,
          items: [
            {
              title: 'Appearance',
              url: '/settings/appearance',
              icon: IconPalette,
            },
          ],
        },
      ],
    },
  ],
}
