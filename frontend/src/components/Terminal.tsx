'use client'

import { useState, useRef, useEffect } from 'react'
import FileUpload from './FileUpload'

interface Message {
  id: number
  type: 'system' | 'user' | 'success' | 'error' | 'info'
  content: string
  timestamp: Date
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
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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

  const handleFilesSelected = async (files: File[]) => {
    setIsProcessing(true)
    setActiveTab('results')
    
    addMessage('user', `Processing ${files.length} file(s)...`)
    files.forEach((file) => {
      addMessage('info', `📄 ${file.name} (${(file.size / 1024).toFixed(2)} KB)`)
    })

    try {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        addMessage('success', '✓ Files processed successfully!')
        
        if (data.filesReceived) {
          addMessage('info', `Files processed: ${data.filesReceived}`)
        }

        if (data.outputFile) {
          addMessage('success', `✓ Output: ${data.outputFile}`)
        }

        if (data.errorLog) {
          addMessage('info', `Error log generated: ${data.errorLog}`)
        }
      } else {
        addMessage('error', `Error: ${data.error || 'Processing failed'}`)
      }
    } catch (error) {
      addMessage('error', `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsProcessing(false)
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
              />
            </div>
          ) : (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Processing Results</h2>
              
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
