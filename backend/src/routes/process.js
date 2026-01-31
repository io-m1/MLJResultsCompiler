const express = require('express')
const path = require('path')
const { processCompleteJob } = require('../utils/excelProcessor')

const router = express.Router()
const uploadsDir = path.join(__dirname, '../../uploads')

// Store processing jobs in memory (in production, use database)
const jobs = new Map()

// POST /api/process - Process uploaded Excel files
router.post('/process', async (req, res, next) => {
  try {
    const { files } = req.body

    if (!files || !Array.isArray(files) || files.length === 0) {
      return res.status(400).json({
        error: true,
        message: 'No files specified for processing'
      })
    }

    if (files.length !== 5) {
      return res.status(400).json({
        error: true,
        message: `Need exactly 5 test files. Received ${files.length}.`
      })
    }

    // Create file paths
    const filePaths = files.map(filename => path.join(uploadsDir, filename))

    // Generate job ID
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    console.log(`📊 Starting job ${jobId} with ${files.length} files`)

    // Store job info
    jobs.set(jobId, {
      id: jobId,
      status: 'processing',
      startedAt: new Date(),
      inputFiles: files
    })

    // Process files asynchronously
    setImmediate(async () => {
      try {
        const result = await processCompleteJob(filePaths)

        if (result.success) {
          jobs.set(jobId, {
            id: jobId,
            status: 'complete',
            startedAt: jobs.get(jobId).startedAt,
            completedAt: new Date(),
            inputFiles: files,
            resultFile: result.resultFile,
            participantCount: result.participantCount,
            passCount: result.passCount,
            failCount: result.failCount
          })
          console.log(`✅ Job ${jobId} completed successfully`)
        } else {
          jobs.set(jobId, {
            id: jobId,
            status: 'error',
            startedAt: jobs.get(jobId).startedAt,
            inputFiles: files,
            error: result.error
          })
          console.log(`❌ Job ${jobId} failed: ${result.error}`)
        }
      } catch (error) {
        console.error(`❌ Job ${jobId} error:`, error)
        jobs.set(jobId, {
          id: jobId,
          status: 'error',
          startedAt: jobs.get(jobId).startedAt,
          inputFiles: files,
          error: error.message
        })
      }
    })

    res.status(202).json({
      success: true,
      jobId: jobId,
      status: 'processing',
      message: 'Processing started',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Process error:', error)
    res.status(500).json({
      error: true,
      message: error.message || 'Processing failed'
    })
  }
})

// GET /api/process-status/:jobId - Check processing status
router.get('/process-status/:jobId', (req, res) => {
  const { jobId } = req.params
  const job = jobs.get(jobId)

  if (!job) {
    return res.status(404).json({
      error: true,
      message: 'Job not found'
    })
  }

  res.json({
    success: true,
    job: {
      id: job.id,
      status: job.status,
      startedAt: job.startedAt,
      completedAt: job.completedAt,
      participantCount: job.participantCount,
      passCount: job.passCount,
      failCount: job.failCount,
      error: job.error
    },
    timestamp: new Date().toISOString()
  })
})

module.exports = router
