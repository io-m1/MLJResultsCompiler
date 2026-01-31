const express = require('express')
const multer = require('multer')
const path = require('path')
const { v4: uuidv4 } = require('uuid')
const { validateExcelFile, validateExcelStructure } = require('../utils/validators')
const { readExcelFile } = require('../utils/excelProcessor')

const router = express.Router()

// Configure multer for file uploads
const uploadsDir = path.join(__dirname, '../../uploads')
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir)
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname)
    const filename = `${uuidv4()}${ext}`
    cb(null, filename)
  }
})

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    if (!file.originalname.toLowerCase().endsWith('.xlsx')) {
      return cb(new Error('File must be Excel format (.xlsx)'))
    }
    cb(null, true)
  }
})

// POST /api/upload - Upload Excel files
router.post('/upload', upload.array('files', 5), async (req, res, next) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({
        error: true,
        message: 'No files uploaded'
      })
    }

    // Validate each uploaded file
    const uploadedFiles = []
    for (const file of req.files) {
      const filePath = path.join(uploadsDir, file.filename)
      
      // Validate Excel format
      const validation = validateExcelFile(filePath)
      if (!validation.isValid) {
        return res.status(400).json({
          error: true,
          message: validation.error
        })
      }

      // Validate sheet structure
      const sheetData = readExcelFile(filePath)
      const structureValidation = validateExcelStructure(sheetData)
      if (!structureValidation.isValid) {
        return res.status(400).json({
          error: true,
          message: structureValidation.error
        })
      }

      uploadedFiles.push({
        originalName: file.originalname,
        storedName: file.filename,
        size: file.size,
        rowCount: structureValidation.rowCount
      })
    }

    // Calculate total size
    const totalSize = uploadedFiles.reduce((sum, f) => sum + f.size, 0)
    const totalSizeMB = (totalSize / 1024 / 1024).toFixed(2)

    console.log(`✅ Upload successful - ${uploadedFiles.length} file(s), ${totalSizeMB} MB`)

    res.status(200).json({
      success: true,
      uploadedCount: uploadedFiles.length,
      totalSize: totalSize,
      totalSizeMB: parseFloat(totalSizeMB),
      files: uploadedFiles,
      status: 'ready_for_processing',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Upload error:', error)
    res.status(500).json({
      error: true,
      message: error.message || 'Upload failed'
    })
  }
})

module.exports = router
