import { z } from 'zod'

// Business schema definition
export const businessSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  address: z.string().nullable(),
  phone_number: z.string().nullable(),
  email: z.string().nullable(),
  customer: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
})

export type Business = z.infer<typeof businessSchema> 