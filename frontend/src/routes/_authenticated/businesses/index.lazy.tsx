import { createLazyFileRoute } from '@tanstack/react-router'
import Businesses from '@/features/businesses'

export const Route = createLazyFileRoute('/_authenticated/businesses/')({
  component: BusinessesPage,
})

function BusinessesPage() {
  return <Businesses />
} 