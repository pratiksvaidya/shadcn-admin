import { useEffect, useState } from 'react'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAgency } from '@/features/auth/context/agency-context'
import { fetchBusiness, fetchBusinessPolicies, fetchBusinessDocuments } from '@/features/businesses/data/api'
import { Business } from '@/features/businesses/data/schema'
import { Policy, PolicyDocument } from '@/features/policies/data/schema'
import { Document } from '@/features/businesses/data/types'
import { IconArrowLeft, IconEdit, IconFileText } from '@tabler/icons-react'
import { Loader2 } from 'lucide-react'
import { format } from 'date-fns'
import { Badge } from '@/components/ui/badge'

export const Route = createFileRoute('/_authenticated/businesses/$businessId')({
  component: BusinessDetail,
})

function BusinessDetail() {
  const { businessId } = Route.useParams()
  const [business, setBusiness] = useState<Business | null>(null)
  const [policies, setPolicies] = useState<Policy[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { selectedAgency } = useAgency()
  const navigate = useNavigate()

  useEffect(() => {
    async function loadBusinessData() {
      if (!selectedAgency || !businessId) return

      setLoading(true)
      setError(null)

      try {
        const businessData = await fetchBusiness(selectedAgency.id, parseInt(businessId))
        setBusiness(businessData)

        // Fetch policies for this business
        const policiesData = await fetchBusinessPolicies(selectedAgency.id, parseInt(businessId))
        setPolicies(policiesData)

        // Fetch documents for this business
        const documentsData = await fetchBusinessDocuments(selectedAgency.id, parseInt(businessId))
        setDocuments(documentsData)
      } catch (err) {
        console.error('Error loading business data:', err)
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    loadBusinessData()
  }, [businessId, selectedAgency])

  const handleBack = () => {
    navigate({ to: '/businesses' })
  }

  if (loading) {
    return (
      <>
        <Header fixed>
          <Search />
          <div className='ml-auto flex items-center space-x-4'>
            <ThemeSwitch />
            <ProfileDropdown />
          </div>
        </Header>
        <Main>
          <div className="flex h-full items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </Main>
      </>
    )
  }

  if (error) {
    return (
      <>
        <Header fixed>
          <Search />
          <div className='ml-auto flex items-center space-x-4'>
            <ThemeSwitch />
            <ProfileDropdown />
          </div>
        </Header>
        <Main>
          <div className="flex h-full flex-col items-center justify-center gap-4">
            <p className="text-destructive">{error}</p>
            <Button variant="outline" onClick={handleBack}>
              Go Back
            </Button>
          </div>
        </Main>
      </>
    )
  }

  if (!business) {
    return (
      <>
        <Header fixed>
          <Search />
          <div className='ml-auto flex items-center space-x-4'>
            <ThemeSwitch />
            <ProfileDropdown />
          </div>
        </Header>
        <Main>
          <div className="flex h-full flex-col items-center justify-center gap-4">
            <p>Business not found</p>
            <Button variant="outline" onClick={handleBack}>
              Go Back
            </Button>
          </div>
        </Main>
      </>
    )
  }

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch (e) {
      return 'Invalid date';
    }
  };

  return (
    <>
      <Header fixed>
        <Search />
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <div className='mb-4 flex items-center gap-4'>
          <Button variant='outline' size='icon' onClick={handleBack}>
            <IconArrowLeft className='h-4 w-4' />
          </Button>
          <div className='flex-1'>
            <h2 className='text-2xl font-bold tracking-tight'>
              {business?.name || 'Business Details'}
            </h2>
            <p className='text-muted-foreground'>
              View and manage business details
            </p>
          </div>
          <Button variant='outline' className='gap-1'>
            <IconEdit className='h-4 w-4' />
            Edit
          </Button>
        </div>

        <Tabs defaultValue='details'>
          <TabsList className='mb-4'>
            <TabsTrigger value='details'>Details</TabsTrigger>
            <TabsTrigger value='policies'>Policies</TabsTrigger>
            <TabsTrigger value='documents'>Documents</TabsTrigger>
          </TabsList>

          <TabsContent value='details' className='space-y-4'>
            <Card>
              <CardHeader>
                <CardTitle>Business Information</CardTitle>
                <CardDescription>Basic details about the business</CardDescription>
              </CardHeader>
              <CardContent className='grid gap-6 sm:grid-cols-2 lg:grid-cols-3'>
                <div className='space-y-1'>
                  <h3 className='text-sm font-medium leading-none text-muted-foreground'>Name</h3>
                  <p className='text-sm'>{business.name}</p>
                </div>
                <div className='space-y-1'>
                  <h3 className='text-sm font-medium leading-none text-muted-foreground'>Email</h3>
                  <p className='text-sm'>{business.email || 'N/A'}</p>
                </div>
                <div className='space-y-1'>
                  <h3 className='text-sm font-medium leading-none text-muted-foreground'>Phone</h3>
                  <p className='text-sm'>{business.phone_number || 'N/A'}</p>
                </div>
                <div className='space-y-1'>
                  <h3 className='text-sm font-medium leading-none text-muted-foreground'>Address</h3>
                  <p className='text-sm'>{business.address || 'N/A'}</p>
                </div>
                <div className='space-y-1'>
                  <h3 className='text-sm font-medium leading-none text-muted-foreground'>Description</h3>
                  <p className='text-sm'>{business.description || 'N/A'}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='policies' className='space-y-4'>
            <Card>
              <CardHeader>
                <CardTitle>Policies</CardTitle>
                <CardDescription>Insurance policies for this business</CardDescription>
              </CardHeader>
              <CardContent>
                {policies.length === 0 ? (
                  <p className='text-sm text-muted-foreground'>No policies found for this business.</p>
                ) : (
                  <div className='grid gap-4'>
                    {policies.map((policy) => (
                      <div key={policy.id} className='rounded-lg border p-4'>
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className='font-medium'>
                              {policy.policy_type_display || policy.policy_type || 'Policy'} 
                              {policy.policy_number ? ` #${policy.policy_number}` : ''}
                            </h3>
                            <p className='text-sm text-muted-foreground'>
                              {policy.carrier ? `Carrier: ${policy.carrier}` : ''}
                              {policy.annual_premium ? ` • Premium: $${policy.annual_premium.toLocaleString()}` : ''}
                            </p>
                          </div>
                          <Badge variant={policy.is_active ? "default" : "outline"}>
                            {policy.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
                          <div>
                            <span className="text-muted-foreground">Effective: </span>
                            {formatDate(policy.effective_date)}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Expires: </span>
                            {formatDate(policy.expiration_date)}
                          </div>
                        </div>
                        
                        {policy.documents && policy.documents.length > 0 && (
                          <div className="mb-3">
                            <h4 className="text-sm font-medium mb-1">Documents</h4>
                            <div className="flex flex-wrap gap-2">
                              {policy.documents.map((doc: PolicyDocument) => (
                                <Badge key={doc.id} variant="outline" className="flex items-center gap-1">
                                  <IconFileText size={14} />
                                  <a 
                                    href={doc.file} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="hover:underline"
                                  >
                                    {doc.name}
                                  </a>
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className='mt-2'>
                          <Button variant='outline' size='sm' onClick={() => navigate({ 
                            to: '/policies/$policyId',
                            params: { policyId: policy.id.toString() }
                          })}>
                            View Details
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='documents' className='space-y-4'>
            <Card>
              <CardHeader>
                <CardTitle>Documents</CardTitle>
                <CardDescription>Documents related to this business</CardDescription>
              </CardHeader>
              <CardContent>
                {documents.length === 0 ? (
                  <p className='text-sm text-muted-foreground'>No documents found for this business.</p>
                ) : (
                  <div className='grid gap-4'>
                    {documents.map((document) => (
                      <div key={document.id} className='rounded-lg border p-4'>
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className='font-medium'>{document.name}</h3>
                            <p className='text-sm text-muted-foreground'>
                              Uploaded: {formatDate(document.created_at)}
                            </p>
                          </div>
                          <IconFileText size={20} className="text-muted-foreground" />
                        </div>
                        <div className='mt-2'>
                          <Button variant='outline' size='sm' asChild>
                            <a href={document.file} target='_blank' rel='noopener noreferrer'>
                              Download
                            </a>
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </Main>
    </>
  )
} 