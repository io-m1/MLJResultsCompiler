const express = require('express')
const fs = require('fs')
const path = require('path')

const router = express.Router()
const uploadsDir = path.join(__dirname, '../../uploads')

// Global jobs storage (in production, use database)
const jobs = new Map()

// GET /api/download/:jobId - Download result file
router.get('/download/:jobId', (req, res) => {
  try {
    const { jobId } = req.params
    const job = jobs.get(jobId)

    if (!job) {
      return res.status(404).json({
        error: true,
        message: 'Job not found'
      })
    }

    if (job.status !== 'complete') {
      return res.status(400).json({
        error: true,
        message: `Cannot download: job status is "${job.status}"`
      })
    }

    if (!job.resultFile) {
      return res.status(404).json({
        error: true,
        message: 'Result file not found'
      })
    }

    // Check if file exists
    if (!fs.existsSync(job.resultFile)) {
      return res.status(404).json({
        error: true,
        message: 'Result file has been deleted'
      })
    }

    // Stream the file
    const fileName = path.basename(job.resultFile)
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`)

    const stream = fs.createReadStream(job.resultFile)
    stream.pipe(res)

    stream.on('error', (error) => {
      console.error('Stream error:', error)
      res.status(500).json({
        error: true,
        message: 'Error reading file'
      })
    })
  } catch (error) {
    console.error('Download error:', error)
    res.status(500).json({
      error: true,
      message: error.message || 'Download failed'
    })
  }
})

// Export jobs for use in other modules
router.getJobs = () => jobs
router.addJob = (jobId, jobData) => jobs.set(jobId, jobData)
router.updateJob = (jobId, jobData) => jobs.set(jobId, { ...jobs.get(jobId), ...jobData })
router.getJob = (jobId) => jobs.get(jobId)

module.exports = router
