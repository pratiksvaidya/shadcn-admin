import { QueryClient } from '@tanstack/react-query'
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
// import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { Toaster } from '@/components/ui/toaster'
import GeneralError from '@/features/errors/general-error'
import NotFoundError from '@/features/errors/not-found-error'
import { AuthProvider } from '@/features/auth/context/auth-context'
import { AgencyProvider } from '@/features/auth/context/agency-context'

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient
}>()({
  component: () => {
    return (
      <AuthProvider>
        <AgencyProvider>
          <Outlet />
          <Toaster />
          {import.meta.env.MODE === 'development' && (
            <>
              {/* <ReactQueryDevtools buttonPosition='bottom-left' /> */}
              {/* <TanStackRouterDevtools position='bottom-right' /> */}
            </>
          )}
        </AgencyProvider>
      </AuthProvider>
    )
  },
  notFoundComponent: NotFoundError,
  errorComponent: GeneralError,
})
