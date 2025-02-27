import { createContext, useContext, useState } from 'react'
import { Customer } from '../data/schema'

type DialogType = 'create' | 'update' | 'delete'

interface CustomersContextType {
  open: DialogType | null
  setOpen: (open: DialogType | null) => void
  currentRow: Customer | null
  setCurrentRow: (row: Customer | null) => void
}

const CustomersContext = createContext<CustomersContextType | null>(null)

interface CustomersProviderProps {
  children: React.ReactNode
}

export default function CustomersProvider({ children }: CustomersProviderProps) {
  const [open, setOpen] = useState<DialogType | null>(null)
  const [currentRow, setCurrentRow] = useState<Customer | null>(null)

  return (
    <CustomersContext.Provider
      value={{
        open,
        setOpen,
        currentRow,
        setCurrentRow,
      }}
    >
      {children}
    </CustomersContext.Provider>
  )
}

export function useCustomers() {
  const context = useContext(CustomersContext)
  if (!context) {
    throw new Error('useCustomers must be used within a CustomersProvider')
  }
  return context
}
