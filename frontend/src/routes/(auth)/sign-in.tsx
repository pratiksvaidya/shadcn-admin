import { createFileRoute } from '@tanstack/react-router'
import SignIn from '@/features/auth/sign-in'
import { z } from 'zod'

export const Route = createFileRoute('/(auth)/sign-in')({
  component: SignIn,
  validateSearch: z.object({
    redirect: z.string().optional(),
  }),
})
