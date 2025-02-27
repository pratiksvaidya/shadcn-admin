import { useState } from "react"
import { FileUpload } from "@/components/ui/file-upload"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { uploadPolicyDocument } from "../data/api"
import { toast } from "@/hooks/use-toast"
import { IconUpload, IconAlertCircle, IconInfoCircle } from "@tabler/icons-react"

interface DocumentUploadProps {
  policyId: number
  agencyId: number
  onSuccess: () => void
}

export function DocumentUpload({ policyId, agencyId, onSuccess }: DocumentUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [debugInfo, setDebugInfo] = useState<string | null>(null)

  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        title: "No file selected",
        description: "Please select a file to upload",
        variant: "destructive",
      })
      return
    }

    try {
      setIsUploading(true)
      setUploadError(null)
      setDebugInfo(null)
      
      // Log file details for debugging
      const fileInfo = {
        name: files[0].name,
        type: files[0].type,
        size: files[0].size,
        policyId,
        agencyId
      }
      
      console.log("Uploading file:", fileInfo)
      setDebugInfo(`Uploading ${fileInfo.name} (${fileInfo.size} bytes) to policy ${policyId}`)
      
      await uploadPolicyDocument(policyId, agencyId, files[0], name, description)
      
      // Reset form
      setFiles([])
      setName("")
      setDescription("")
      setDebugInfo(null)
      
      toast({
        title: "Document uploaded",
        description: "The document has been uploaded successfully",
      })
      
      // Notify parent component to refresh documents
      onSuccess()
    } catch (error) {
      console.error("Upload error:", error)
      
      const errorMessage = error instanceof Error ? error.message : "Failed to upload document"
      setUploadError(errorMessage)
      
      toast({
        title: "Upload failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="document-name">Document Name (Optional)</Label>
        <Input
          id="document-name"
          placeholder="Enter document name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="document-description">Description (Optional)</Label>
        <Textarea
          id="document-description"
          placeholder="Enter document description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
        />
      </div>
      
      <div className="space-y-2">
        <Label>File</Label>
        <FileUpload
          value={files}
          onChange={setFiles}
          dropzoneOptions={{
            maxFiles: 1,
            maxSize: 10 * 1024 * 1024, // 10MB
            accept: {
              'application/pdf': ['.pdf'],
              'image/*': ['.png', '.jpg', '.jpeg'],
              'application/msword': ['.doc'],
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
              'application/vnd.ms-excel': ['.xls'],
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
            }
          }}
        />
      </div>
      
      {debugInfo && (
        <div className="rounded-md bg-blue-50 p-3 text-sm text-blue-700">
          <div className="flex items-center gap-2">
            <IconInfoCircle className="h-4 w-4" />
            <p className="font-medium">Upload info:</p>
          </div>
          <p className="mt-1">{debugInfo}</p>
        </div>
      )}
      
      {uploadError && (
        <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
          <div className="flex items-center gap-2">
            <IconAlertCircle className="h-4 w-4" />
            <p className="font-medium">Error uploading document:</p>
          </div>
          <p className="mt-1">{uploadError}</p>
          {uploadError.includes('404') && (
            <p className="mt-2 text-xs">
              The upload endpoint was not found. Please check that your backend server is running and the API endpoint exists.
            </p>
          )}
          {uploadError.includes('401') && (
            <p className="mt-2 text-xs">
              Authentication error. Try logging out and logging back in.
            </p>
          )}
          {uploadError.includes('415') && (
            <p className="mt-2 text-xs">
              The server doesn't accept the file format or content type. This is likely a problem with how the request is being sent.
            </p>
          )}
          {uploadError.includes('undefined') && (
            <p className="mt-2 text-xs">
              There was an issue with the Content-Type header. We've updated the code to fix this issue.
            </p>
          )}
        </div>
      )}
      
      <Button 
        onClick={handleUpload} 
        disabled={isUploading || files.length === 0}
        className="w-full"
      >
        {isUploading ? (
          "Uploading..."
        ) : (
          <>
            <IconUpload className="mr-2 h-4 w-4" />
            Upload Document
          </>
        )}
      </Button>
    </div>
  )
} 