require('dotenv').config()
const express = require('express')
const cors = require('cors')
const path = require('path')
const fs = require('fs')

// Import routes
const uploadRoutes = require('./routes/upload')
const processRoutes = require('./routes/process')
const downloadRoutes = require('./routes/download')
const historyRoutes = require('./routes/history')

// Import middleware
const errorHandler = require('./middleware/errorHandler')
const requestLogger = require('./middleware/requestLogger')

const app = express()
const PORT = process.env.PORT || 3000

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, '../uploads')
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true })
  console.log('✓ Created uploads directory')
}

// Middleware
app.use(requestLogger)
app.use(cors({
  origin: process.env.CORS_ORIGIN || ['http://localhost:3000', 'https://mljresultscompiler.vercel.app'],
  credentials: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// API Routes
app.use('/api', uploadRoutes)
app.use('/api', processRoutes)
app.use('/api', downloadRoutes)
app.use('/api', historyRoutes)

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.path}`,
    timestamp: new Date().toISOString()
  })
})

// Error handling middleware (must be last)
app.use(errorHandler)

// Start server
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║    MLJ Results Compiler Backend - Node.js Express          ║
╠════════════════════════════════════════════════════════════╣
║  Server running on port ${PORT}
║  Environment: ${process.env.NODE_ENV || 'development'}
║  CORS enabled for: ${process.env.CORS_ORIGIN || 'localhost:3000'}
║                                                             ║
║  Endpoints:                                                ║
║  POST   /api/upload              - Upload Excel files      ║
║  POST   /api/process             - Process uploaded files  ║
║  GET    /api/history             - View processing history ║
║  GET    /api/download/:jobId     - Download result file   ║
║  GET    /health                  - Health check           ║
╚════════════════════════════════════════════════════════════╝
  `)
})

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server')
  process.exit(0)
})
