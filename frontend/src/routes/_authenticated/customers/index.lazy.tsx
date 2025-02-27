import { createLazyFileRoute } from '@tanstack/react-router'
import Customers from '@/features/customers'

export const Route = createLazyFileRoute('/_authenticated/customers/')({
  component: Customers,
})
