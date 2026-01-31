const express = require('express')

const router = express.Router()

// Global jobs storage (shared with process.js)
let jobsStore = new Map()

// Helper to set jobs reference from process route
router.setJobsStore = (jobs) => {
  jobsStore = jobs
}

// GET /api/history - Get processing history
router.get('/history', (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50
    
    // Convert map to array and sort by date
    const jobArray = Array.from(jobsStore.values())
      .sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt))
      .slice(0, limit)

    // Format response
    const formattedJobs = jobArray.map(job => ({
      id: job.id,
      status: job.status,
      uploadedAt: job.startedAt,
      processedAt: job.completedAt,
      inputFiles: job.inputFiles || [],
      participantCount: job.participantCount || 0,
      passCount: job.passCount || 0,
      failCount: job.failCount || 0,
      error: job.error || null
    }))

    res.json({
      success: true,
      totalJobs: jobArray.length,
      jobs: formattedJobs,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('History error:', error)
    res.status(500).json({
      error: true,
      message: error.message || 'Failed to retrieve history'
    })
  }
})

module.exports = router
