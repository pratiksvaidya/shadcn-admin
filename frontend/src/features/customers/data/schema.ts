import { z } from 'zod'

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const customerSchema = z.object({
  id: z.number(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string().email(),
  phone_number: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  businesses: z.array(z.any()).optional()
})

export type Customer = z.infer<typeof customerSchema>
