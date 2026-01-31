'use client'

import { useState, useRef, useEffect } from 'react'
import FileUpload from './FileUpload'

interface Message {
  id: number
  type: 'system' | 'user' | 'success' | 'error' | 'info'
  content: string
  timestamp: Date
}

interface ProcessingJob {
  jobId: string
  status: 'processing' | 'complete' | 'error'
  participantCount?: number
  passCount?: number
  failCount?: number
}

export default function Terminal() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'system',
      content: 'Welcome to MLJ Results Compiler',
      timestamp: new Date(),
    },
    {
      id: 2,
      type: 'info',
      content: 'Upload your test result files to begin automated compilation.',
      timestamp: new Date(),
    },
  ])

  const [isProcessing, setIsProcessing] = useState(false)
  const [activeTab, setActiveTab] = useState<'upload' | 'results'>('upload')
  const [currentJob, setCurrentJob] = useState<ProcessingJob | null>(null)
  const [uploadedFileIds, setUploadedFileIds] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const statusCheckInterval = useRef<NodeJS.Timeout | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current)
      }
    }
  }, [])

  useEffect(() => {
    if (!currentJob || currentJob.status !== 'processing') return

    const checkStatus = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'
        const response = await fetch(`${apiUrl}/api/process-status/${currentJob.jobId}`)
        const data = await response.json()

        setCurrentJob((prev) =>
          prev
            ? {
                ...prev,
                status: data.status,
                participantCount: data.participantCount,
                passCount: data.passCount,
                failCount: data.failCount,
              }
            : null
        )

        if (data.status === 'complete') {
          addMessage('success', `✓ Processing completed! ${data.participantCount} participants processed.`)
          addMessage('info', `📈 Results: ${data.passCount} passed, ${data.failCount} failed`)
          setIsProcessing(false)
        } else if (data.status === 'error') {
          addMessage('error', `✗ Processing failed: ${data.error || 'Unknown error'}`)
          setIsProcessing(false)
        }
      } catch (error) {
        console.error('Status check error:', error)
      }
    }

    statusCheckInterval.current = setInterval(checkStatus, 2000)
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current)
      }
    }
  }, [currentJob])

  const addMessage = (type: Message['type'], content: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type,
        content,
        timestamp: new Date(),
      },
    ])
  }

  const handleFilesSelected = async (files: File[], uploadedIds: string[]) => {
    setUploadedFileIds(uploadedIds)
    setIsProcessing(true)
    setActiveTab('results')

    addMessage('user', `✓ Uploaded ${files.length} file(s) successfully`)
    files.forEach((file) => {
      addMessage('info', `📄 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`)
    })

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'
      
      const response = await fetch(`${apiUrl}/api/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileIds: uploadedIds }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Processing failed')
      }

      const data = await response.json()

      if (!data.jobId) {
        throw new Error('No job ID returned')
      }

      setCurrentJob({
        jobId: data.jobId,
        status: 'processing',
      })

      addMessage('system', `⏳ Processing started (Job ID: ${data.jobId.substring(0, 8)}...)`)
      addMessage('info', 'Merging test results and calculating scores...')
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Processing failed'
      addMessage('error', `✗ Error: ${errorMessage}`)
      setIsProcessing(false)
    }
  }

  const handleDownload = async () => {
    if (!currentJob?.jobId) return

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'
      const downloadUrl = `${apiUrl}/api/download/${currentJob.jobId}`
      window.location.href = downloadUrl
      addMessage('success', '✓ Download started')
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Download failed'
      addMessage('error', `✗ Download error: ${errorMessage}`)
    }
  }

  const getMessageColor = (type: Message['type']) => {
    switch (type) {
      case 'system':
        return 'text-gray-700'
      case 'user':
        return 'text-brand-primary font-semibold'
      case 'success':
        return 'text-green-600 font-semibold'
      case 'error':
        return 'text-red-600 font-semibold'
      case 'info':
        return 'text-gray-600'
      default:
        return 'text-gray-700'
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Navigation Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-primary to-brand-secondary flex items-center justify-center text-white font-bold text-lg">
                📊
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MLJ Results Compiler</h1>
                <p className="text-xs text-gray-600">Automated Test Result Compilation</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              {isProcessing && (
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin text-brand-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Processing...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('upload')}
              className={`py-4 px-2 font-semibold transition-colors border-b-2 ${ 
                activeTab === 'upload'
                  ? 'text-brand-primary border-brand-primary'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              📤 Upload Files
            </button>
            <button
              onClick={() => setActiveTab('results')}
              className={`py-4 px-2 font-semibold transition-colors border-b-2 ${
                activeTab === 'results'
                  ? 'text-brand-primary border-brand-primary'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              📊 Results
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {activeTab === 'upload' ? (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload XLS Files</h2>
              <p className="text-gray-600 mb-8">Select your test result files to begin automated compilation</p>
              <FileUpload 
                onFilesSelected={handleFilesSelected} 
                disabled={isProcessing}
                onUploadStart={() => addMessage('info', '📤 Uploading files to server...')}
                onUploadError={(error) => {
                  addMessage('error', `✗ Upload error: ${error}`)
                  setIsProcessing(false)
                }}
              />
            </div>
          ) : (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Processing Results</h2>
              
              {/* Processing Status */}
              {currentJob && (
                <div className="mb-6 bg-gradient-to-r from-brand-secondary/10 to-brand-primary/10 border border-brand-primary/30 rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-gray-900">Job Status</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {currentJob.status === 'processing' && '⏳ Processing in progress...'}
                        {currentJob.status === 'complete' && '✓ Processing completed'}
                        {currentJob.status === 'error' && '✗ Processing failed'}
                      </p>
                    </div>
                    {currentJob.status === 'processing' && (
                      <svg className="w-6 h-6 animate-spin text-brand-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    )}
                  </div>

                  {currentJob.status === 'complete' && (
                    <div className="mt-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-700">Participants:</span>
                        <span className="font-bold text-gray-900">{currentJob.participantCount}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-700">Passed:</span>
                        <span className="font-bold text-green-600">{currentJob.passCount}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-700">Failed:</span>
                        <span className="font-bold text-red-600">{currentJob.failCount}</span>
                      </div>

                      <button
                        onClick={handleDownload}
                        className="w-full mt-4 py-3 px-4 bg-gradient-to-r from-green-500 to-green-600 text-white font-bold rounded-lg hover:shadow-lg transition-all flex items-center justify-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                        Download Excel Results
                      </button>
                    </div>
                  )}
                </div>
              )}
              
              {/* Messages Area */}
              <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-3 max-h-96 overflow-y-auto">
                {messages.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No processing history yet. Upload files to begin.</p>
                ) : (
                  <>
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`text-sm py-2 pl-3 border-l-4 ${
                          message.type === 'success' ? 'border-green-500 bg-green-50' :
                          message.type === 'error' ? 'border-red-500 bg-red-50' :
                          message.type === 'user' ? 'border-brand-primary bg-brand-primary/5' :
                          'border-gray-300 bg-gray-50'
                        }`}
                      >
                        <div className={`${getMessageColor(message.type)}`}>
                          {message.content}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
