import { createFileRoute } from '@tanstack/react-router'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { LoadingSpinner } from '@/components/loading-spinner'
import { useAgency } from '@/features/auth/context/agency-context'
import { useEffect, useState } from 'react'
import { Policy } from '@/features/policies/components/columns'
import { Button } from '@/components/ui/button'
import { IconArrowLeft, IconFileText, IconDownload, IconFile, IconPlus, IconTrash, IconRefresh, IconArrowUp, IconArrowDown } from '@tabler/icons-react'
import { Badge } from '@/components/ui/badge'
import { format, isValid } from 'date-fns'
import { fetchPolicy, removePolicyDocument, generateRenewalComparison, RenewalComparison } from '@/features/policies/data/api'
import { toast } from '@/hooks/use-toast'
import { useNavigate } from '@tanstack/react-router'
import { DocumentUpload } from '@/features/policies/components/document-upload'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { marked } from 'marked'

export const Route = createFileRoute('/_authenticated/policies/$policyId')({
  component: PolicyDetail,
})

function PolicyDetail() {
  const { policyId } = Route.useParams()
  const { selectedAgency } = useAgency()
  const [policy, setPolicy] = useState<Policy | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false)
  const [isRemovingDocument, setIsRemovingDocument] = useState(false)
  const [isRenewalDialogOpen, setIsRenewalDialogOpen] = useState(false)
  const [renewalComparison, setRenewalComparison] = useState<RenewalComparison | null>(null)
  const [isGeneratingRenewal, setIsGeneratingRenewal] = useState(false)
  const [aiProvider, setAiProvider] = useState<'anthropic' | 'openai'>('openai')
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('email')

  const loadPolicy = async () => {
    if (!selectedAgency) {
      setError('Please select an agency to view policy details')
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      const policyData = await fetchPolicy(selectedAgency.id, parseInt(policyId))
      if (!policyData) {
        throw new Error('Policy not found')
      }
      setPolicy(policyData)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load policy')
      console.error('Error loading policy:', err)
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to load policy',
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPolicy()
  }, [policyId, selectedAgency])

  // Format policy type for display
  const formatPolicyType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  // Format currency
  const formatCurrency = (amount: number | null) => {
    if (amount === null || isNaN(amount)) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  }

  // Format date safely
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not set';
    
    const date = new Date(dateString);
    if (!isValid(date)) return 'Invalid date';
    
    return format(date, 'MMMM d, yyyy');
  }

  const handleBackClick = () => {
    navigate({ to: '/policies' })
  }

  const handleRemoveDocument = async (documentId: number) => {
    if (!selectedAgency || !policy) return;
    
    try {
      setIsRemovingDocument(true);
      await removePolicyDocument(policy.id, documentId, selectedAgency.id);
      
      toast({
        title: "Document removed",
        description: "The document has been removed successfully",
      });
      
      // Refresh policy data
      await loadPolicy();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to remove document",
        variant: "destructive",
      });
    } finally {
      setIsRemovingDocument(false);
    }
  };

  const handleGenerateRenewal = async () => {
    if (!selectedAgency || !policy) return;
    
    try {
      setIsGeneratingRenewal(true);
      const comparison = await generateRenewalComparison(policy.id, selectedAgency.id, aiProvider);
      setRenewalComparison(comparison);
      setIsRenewalDialogOpen(true);
      
      toast({
        title: "Renewal comparison generated",
        description: "The renewal comparison has been generated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate renewal comparison",
        variant: "destructive",
      });
    } finally {
      setIsGeneratingRenewal(false);
    }
  };

  return (
    <>
      <Header fixed>
        <div className='flex items-center gap-2'>
          <Button
            variant='ghost'
            size='sm'
            onClick={handleBackClick}
          >
            <IconArrowLeft className='mr-2 h-4 w-4' />
            Back
          </Button>
          <div>
            <h1 className='text-lg font-semibold'>
              {policy ? formatPolicyType(policy.policy_type) : 'Policy Details'}
            </h1>
            {policy && (
              <p className='text-sm text-muted-foreground'>
                {policy.policy_number || 'No policy number'}
              </p>
            )}
          </div>
        </div>
        <div className='ml-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        {loading ? (
          <div className='flex h-32 items-center justify-center'>
            <LoadingSpinner size='lg' />
          </div>
        ) : error ? (
          <div className='flex h-32 items-center justify-center'>
            <p className='text-red-500'>{error}</p>
          </div>
        ) : policy ? (
          <div className='space-y-6'>
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              <div className='space-y-2'>
                <h2 className='text-lg font-semibold'>Policy Information</h2>
                <div className='rounded-lg border p-4'>
                  <div className='space-y-3'>
                    <div>
                      <label className='text-sm text-muted-foreground'>Policy Type</label>
                      <div className='flex items-center gap-2'>
                        <IconFileText className='h-4 w-4 text-muted-foreground' />
                        <Badge variant='outline' className='capitalize'>
                          {formatPolicyType(policy.policy_type)}
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Policy Number</label>
                      <p>{policy.policy_number || 'N/A'}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Carrier</label>
                      <p>{policy.carrier || 'N/A'}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Annual Premium</label>
                      <p className='font-medium'>{formatCurrency(policy.annual_premium)}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Status</label>
                      <div className='mt-1'>
                        <Badge variant={policy.is_active ? 'default' : 'secondary'}>
                          {policy.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    </div>
                    <div className="pt-2">
                      <div className="flex flex-col space-y-2">
                        <div className="flex flex-col space-y-1 mb-2">
                          <label className="text-sm text-muted-foreground">AI Provider:</label>
                          <Select
                            value={aiProvider}
                            onValueChange={(value) => setAiProvider(value as 'anthropic' | 'openai')}
                            disabled={isGeneratingRenewal}
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Select AI provider" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="openai">OpenAI (o3-mini)</SelectItem>
                              <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Button 
                          variant='outline' 
                          size='sm'
                          className='w-full'
                          onClick={handleGenerateRenewal}
                          disabled={isGeneratingRenewal || !policy.documents || policy.documents.length === 0}
                          title={!policy.documents || policy.documents.length === 0 ? 
                            "Please upload at least one document to generate a renewal comparison" : 
                            "Generate a renewal comparison for this policy"}
                        >
                          {isGeneratingRenewal ? (
                            <>
                              <LoadingSpinner size='sm' className='mr-2' />
                              Generating...
                            </>
                          ) : (
                            <>
                              <IconRefresh className='mr-2 h-4 w-4' />
                              Generate Renewal Comparison
                            </>
                          )}
                        </Button>
                        {(!policy.documents || policy.documents.length === 0) && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Upload documents to enable renewal comparison
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className='space-y-2'>
                <h2 className='text-lg font-semibold'>Dates</h2>
                <div className='rounded-lg border p-4'>
                  <div className='space-y-3'>
                    <div>
                      <label className='text-sm text-muted-foreground'>Effective Date</label>
                      <p>{formatDate(policy.effective_date)}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Expiration Date</label>
                      <p>{formatDate(policy.expiration_date)}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Created</label>
                      <p>{formatDate(policy.created_at)}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Last Updated</label>
                      <p>{formatDate(policy.updated_at)}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className='space-y-2'>
                <h2 className='text-lg font-semibold'>Business Information</h2>
                <div className='rounded-lg border p-4'>
                  <div className='space-y-3'>
                    <div>
                      <label className='text-sm text-muted-foreground'>Business Name</label>
                      <p className='font-medium'>{policy.business.name}</p>
                    </div>
                    <div>
                      <label className='text-sm text-muted-foreground'>Business ID</label>
                      <p>{policy.business.id}</p>
                    </div>
                    <Button 
                      variant='outline' 
                      size='sm' 
                      className='mt-2'
                      onClick={() => navigate({ 
                        to: '/businesses/$businessId', 
                        params: { businessId: policy.business.id.toString() } 
                      })}
                    >
                      View Business Details
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Documents Section */}
            <div className='space-y-2'>
              <div className='flex items-center justify-between'>
                <h2 className='text-lg font-semibold'>Policy Documents</h2>
                {selectedAgency && (
                  <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm" variant="outline">
                        <IconPlus className="mr-2 h-4 w-4" />
                        Upload Document
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Upload Document</DialogTitle>
                      </DialogHeader>
                      <DocumentUpload 
                        policyId={policy.id} 
                        agencyId={selectedAgency.id}
                        onSuccess={() => {
                          setIsUploadDialogOpen(false);
                          loadPolicy();
                        }}
                      />
                    </DialogContent>
                  </Dialog>
                )}
              </div>
              <div className='rounded-lg border p-4'>
                {policy.documents && policy.documents.length > 0 ? (
                  <div className='space-y-3'>
                    {policy.documents.map((document) => (
                      <div key={document.id} className='flex items-center justify-between border-b pb-3'>
                        <div className='flex items-center gap-2'>
                          <IconFile className='h-5 w-5 text-muted-foreground' />
                          <div>
                            <p className='font-medium'>{document.name || `Document #${document.id}`}</p>
                            {document.description && (
                              <p className='text-sm text-muted-foreground'>{document.description}</p>
                            )}
                          </div>
                        </div>
                        <div className='flex items-center gap-2'>
                          <a 
                            href={document.file} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className='flex items-center gap-1 text-sm text-primary hover:underline'
                          >
                            <IconDownload className='h-4 w-4' />
                            Download
                          </a>
                          
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                                <IconTrash className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Remove Document</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to remove this document? This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleRemoveDocument(document.id)}
                                  disabled={isRemovingDocument}
                                >
                                  {isRemovingDocument ? "Removing..." : "Remove"}
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className='flex flex-col items-center justify-center py-6 text-center'>
                    <IconFileText className='h-10 w-10 text-muted-foreground' />
                    <h3 className='mt-2 text-sm font-medium'>No documents</h3>
                    <p className='mt-1 text-sm text-muted-foreground'>
                      There are no documents attached to this policy.
                    </p>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="mt-4"
                      onClick={() => setIsUploadDialogOpen(true)}
                    >
                      <IconPlus className="mr-2 h-4 w-4" />
                      Upload Document
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className='flex h-32 items-center justify-center'>
            <p>Policy not found</p>
          </div>
        )}
      </Main>

      {/* Renewal Comparison Dialog */}
      <Dialog open={isRenewalDialogOpen} onOpenChange={setIsRenewalDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader className="flex-shrink-0">
            <DialogTitle>Policy Renewal Comparison</DialogTitle>
          </DialogHeader>
          
          {renewalComparison && (
            <div className="space-y-4 flex-grow flex flex-col overflow-hidden">
              {/* Tabs */}
              <div className="border-b">
                <div className="flex">
                  <button
                    onClick={() => setActiveTab('email')}
                    className={`px-4 py-2 text-sm font-medium ${
                      activeTab === 'email'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Email Content
                  </button>
                  <button
                    onClick={() => setActiveTab('attachment')}
                    className={`px-4 py-2 text-sm font-medium ${
                      activeTab === 'attachment'
                        ? 'border-b-2 border-primary text-primary'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Detailed Report
                  </button>
                </div>
              </div>
              
              {/* Content Area - Scrollable */}
              <div className="flex-grow overflow-y-auto pr-2">
                {activeTab === 'email' && (
                  <div className="space-y-2">
                    <div className="rounded-lg border p-4 prose prose-sm max-w-none dark:prose-invert">
                      <div className="whitespace-pre-wrap">
                        {renewalComparison.email || 'No email content available.'}
                      </div>
                    </div>
                  </div>
                )}
                
                {activeTab === 'attachment' && (
                  <div className="space-y-2">
                    <div className="rounded-lg border p-4 prose prose-sm max-w-none dark:prose-invert">
                      {renewalComparison.attachment ? (
                        <>
                          <style dangerouslySetInnerHTML={{ __html: `
                            .markdown-content table {
                              font-size: 0.875rem;
                              width: 100%;
                              border-collapse: collapse;
                              margin: 1.5rem 0;
                            }
                            .markdown-content th {
                              background-color: hsl(var(--muted));
                              font-weight: 600;
                              text-align: left;
                              padding: 0.75rem;
                              border: 1px solid hsl(var(--border));
                            }
                            .markdown-content td {
                              padding: 0.75rem;
                              border: 1px solid hsl(var(--border));
                              vertical-align: top;
                            }
                            .markdown-content tr:nth-child(even) {
                              background-color: hsl(var(--muted) / 0.1);
                            }
                            .markdown-content thead {
                              background-color: hsl(var(--muted) / 0.5);
                            }
                            .markdown-content table strong {
                              font-weight: 600;
                            }
                            .markdown-content h1 {
                              font-size: 1.5rem;
                              margin-top: 1.5rem;
                              margin-bottom: 1rem;
                              font-weight: 600;
                            }
                            .markdown-content h2 {
                              font-size: 1.25rem;
                              margin-top: 1.25rem;
                              margin-bottom: 0.75rem;
                              font-weight: 600;
                            }
                            .markdown-content h3 {
                              font-size: 1.125rem;
                              margin-top: 1rem;
                              margin-bottom: 0.5rem;
                              font-weight: 600;
                            }
                            .markdown-content ul, .markdown-content ol {
                              padding-left: 1.5rem;
                              margin: 1rem 0;
                            }
                            .markdown-content li {
                              margin-bottom: 0.25rem;
                            }
                          `}} />
                          <div 
                            className="markdown-content" 
                            dangerouslySetInnerHTML={{ 
                              __html: marked.parse(renewalComparison.attachment, {
                                gfm: true,
                                breaks: true
                              }) 
                            }} 
                          />
                        </>
                      ) : (
                        'No attachment content available.'
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {/* AI Provider Info */}
              {renewalComparison.ai_provider && (
                <div className="text-xs text-muted-foreground text-right mt-2 flex-shrink-0">
                  Generated using: {renewalComparison.ai_provider === 'anthropic' ? 'Anthropic (Claude)' : 'OpenAI (o3-mini)'}
                </div>
              )}
              
              <div className="flex justify-end space-x-2 pt-2 border-t flex-shrink-0">
                <Button variant="outline" onClick={() => setIsRenewalDialogOpen(false)}>Close</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
} 