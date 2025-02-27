import { Button } from '@/components/ui/button'
import { useCustomers } from '../context/customers-context'

export function CustomersPrimaryButtons() {
  const { setOpen } = useCustomers()

  return (
    <div className='flex items-center gap-2'>
      <Button onClick={() => setOpen('create')}>Add Customer</Button>
    </div>
  )
}
