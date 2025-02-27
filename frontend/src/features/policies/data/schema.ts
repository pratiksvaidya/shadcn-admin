import { z } from 'zod'

// Define a document schema for policies
export const policyDocumentSchema = z.object({
  id: z.number(),
  name: z.string(),
  file: z.string().optional(),
  // Add other document fields as needed
})

export const policySchema = z.object({
  id: z.number(),
  business: z.number(),
  policy_number: z.string().nullable(),
  effective_date: z.string().nullable().optional(),
  expiration_date: z.string().nullable().optional(),
  carrier: z.string().nullable().optional(),
  annual_premium: z.number().nullable().optional(),
  policy_type: z.string().optional(),
  policy_type_display: z.string().optional(),
  is_active: z.boolean().optional(),
  documents: z.array(policyDocumentSchema).optional(),
  created_at: z.string(),
  updated_at: z.string(),
})

export type Policy = z.infer<typeof policySchema>
export type PolicyDocument = z.infer<typeof policyDocumentSchema> 