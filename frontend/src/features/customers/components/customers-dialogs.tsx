import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useCustomers } from '../context/customers-context'
import { deleteCustomer } from '../data/customers'
import { useToast } from '@/hooks/use-toast'
import { useAgency } from '@/features/auth/context/agency-context'

export function CustomersDialogs() {
  const { open, setOpen, currentRow } = useCustomers()
  const { selectedAgency } = useAgency()
  const { toast } = useToast()

  const handleDelete = async () => {
    if (!currentRow || !selectedAgency) return

    try {
      await deleteCustomer(currentRow.id, selectedAgency.id)
      toast({
        title: 'Success',
        description: 'Customer deleted successfully.',
      })
      setOpen(null)
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to delete customer',
        variant: 'destructive',
      })
    }
  }

  return (
    <>
      <AlertDialog open={open === 'delete'} onOpenChange={() => setOpen(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the
              customer and all their data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              disabled={!selectedAgency}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
