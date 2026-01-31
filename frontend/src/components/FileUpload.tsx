'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void
  disabled?: boolean
}

export default function FileUpload({ onFilesSelected, disabled }: FileUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const xlsFiles = acceptedFiles.filter((file) => file.name.endsWith('.xls'))
    setSelectedFiles((prev) => [...prev, ...xlsFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.ms-excel': ['.xls'],
    },
    disabled,
    multiple: true,
  })

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      onFilesSelected(selectedFiles)
      setSelectedFiles([])
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="w-full space-y-6">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300
          ${isDragActive 
            ? 'border-brand-primary bg-brand-primary/5 scale-102' 
            : 'border-gray-300 hover:border-brand-primary hover:bg-brand-primary/2'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <div className="space-y-3">
          <div className="text-5xl">📊</div>
          {isDragActive ? (
            <div>
              <p className="text-2xl font-bold text-brand-primary">
                Drop your XLS files here!
              </p>
              <p className="text-gray-600 mt-2">Release to upload</p>
            </div>
          ) : (
            <div>
              <p className="text-2xl font-bold text-gray-800">
                Upload Test Results
              </p>
              <p className="text-gray-600 mt-2">
                Drag & drop XLS files or <span className="text-brand-primary font-semibold">click to browse</span>
              </p>
              <p className="text-sm text-gray-500 mt-3">
                ✓ XLS format only (.xls files)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="bg-gradient-to-br from-brand-secondary/5 to-brand-primary/5 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-800">
              Ready to Process
            </h3>
            <span className="bg-brand-primary text-white text-sm font-bold px-3 py-1 rounded-full">
              {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
            </span>
          </div>

          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-white border border-gray-200 p-4 rounded-xl hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-2xl">📄</span>
                  <div className="flex-1 text-left">
                    <p className="font-semibold text-gray-800">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  disabled={disabled}
                  className="ml-4 p-2 hover:bg-red-50 text-red-500 rounded-lg transition-colors hover:rounded-lg"
                  title="Remove file"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          {/* Compile Button */}
          <button
            onClick={handleUpload}
            disabled={disabled || selectedFiles.length === 0}
            className={`w-full py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-2
              ${
                disabled || selectedFiles.length === 0
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-brand-primary to-brand-secondary text-white hover:shadow-xl hover:shadow-brand-primary/30 active:scale-95 transform'
              }`}
          >
            {disabled ? (
              <>
                <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Compiling...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                Start Compilation
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
