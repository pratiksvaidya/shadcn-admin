import * as React from "react"
import { useDropzone, type DropzoneOptions } from "react-dropzone"
import { twMerge } from "tailwind-merge"

import { Button } from "@/components/ui/button"
import { IconUpload } from "@tabler/icons-react"

const variants = {
  base: "relative rounded-md flex justify-center items-center flex-col cursor-pointer min-h-[150px] border border-dashed border-gray-400 dark:border-gray-300 transition-colors duration-200 ease-in-out",
  active: "border-2",
  disabled: "bg-gray-200 border-gray-300 cursor-default pointer-events-none bg-opacity-30 dark:bg-gray-700",
  accept: "border border-blue-500 bg-blue-500 bg-opacity-10",
  reject: "border border-red-700 bg-red-700 bg-opacity-10",
}

export type FileUploadProps = {
  className?: string
  value?: File[]
  onChange?: (files: File[]) => void | Promise<void>
  onFilesAdded?: (addedFiles: File[]) => void | Promise<void>
  disabled?: boolean
  dropzoneOptions?: Omit<DropzoneOptions, "disabled">
}

const FileUpload = React.forwardRef<HTMLInputElement, FileUploadProps>(
  (
    {
      className,
      value,
      onChange,
      onFilesAdded,
      disabled = false,
      dropzoneOptions,
    },
    ref
  ) => {
    const [files, setFiles] = React.useState<File[]>(value || [])

    React.useEffect(() => {
      if (value) {
        setFiles(value)
      }
    }, [value])

    const onDrop = React.useCallback(
      (acceptedFiles: File[]) => {
        const newFiles = [...files, ...acceptedFiles]
        setFiles(newFiles)
        onChange?.(newFiles)
        onFilesAdded?.(acceptedFiles)
      },
      [files, onChange, onFilesAdded]
    )

    const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
      onDrop,
      disabled,
      ...dropzoneOptions,
    })

    // Styling
    const dropzoneClassName = React.useMemo(
      () =>
        twMerge(
          variants.base,
          isDragActive && variants.active,
          isDragAccept && variants.accept,
          isDragReject && variants.reject,
          disabled && variants.disabled,
          className
        ),
      [isDragActive, isDragAccept, isDragReject, disabled, className]
    )

    return (
      <div>
        <div
          {...getRootProps({
            className: dropzoneClassName,
          })}
        >
          <input ref={ref} {...getInputProps()} />
          <div className="flex flex-col items-center justify-center text-xs text-gray-400">
            <IconUpload className="mb-1 h-7 w-7" />
            <div className="text-gray-400">
              Drag & drop files here, or click to select files
            </div>
          </div>
        </div>

        {/* Preview */}
        {files.length > 0 && (
          <div className="mt-1">
            <div className="text-xs font-medium text-gray-500">Selected files:</div>
            <ul className="mt-1 divide-y divide-gray-200 rounded-md border border-gray-200">
              {files.map((file) => (
                <li
                  key={file.name}
                  className="flex items-center justify-between py-2 pl-3 pr-4 text-sm"
                >
                  <div className="flex w-0 flex-1 items-center">
                    <span className="w-0 flex-1 truncate">{file.name}</span>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const newFiles = files.filter((f) => f !== file)
                        setFiles(newFiles)
                        onChange?.(newFiles)
                      }}
                    >
                      Remove
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )
  }
)
FileUpload.displayName = "FileUpload"

export { FileUpload } 