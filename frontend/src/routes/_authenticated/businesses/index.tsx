import { createFileRoute } from '@tanstack/react-router'
import Businesses from '@/features/businesses'

export const Route = createFileRoute('/_authenticated/businesses/')({
  component: BusinessesPage,
})

function BusinessesPage() {
  return <Businesses />
} 