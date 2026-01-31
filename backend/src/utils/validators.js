const fs = require('fs')
const path = require('path')

// Excel file validation
function validateExcelFile(filePath) {
  try {
    const stats = fs.statSync(filePath)
    
    // Check file extension
    const ext = path.extname(filePath).toLowerCase()
    if (ext !== '.xlsx') {
      return {
        isValid: false,
        error: 'File must be Excel format (.xlsx extension required)'
      }
    }

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024
    if (stats.size > maxSize) {
      return {
        isValid: false,
        error: `File too large (${(stats.size / 1024 / 1024).toFixed(2)} MB). Maximum 10 MB allowed.`
      }
    }

    // Try to read Excel file
    try {
      const XLSX = require('xlsx')
      const workbook = XLSX.readFile(filePath)
      
      if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
        return {
          isValid: false,
          error: 'Excel file has no sheets'
        }
      }

      console.log(`✓ Validated Excel file: ${path.basename(filePath)} - Sheets: ${workbook.SheetNames.join(', ')}`)
      return { isValid: true }
    } catch (excelError) {
      return {
        isValid: false,
        error: 'Excel file corrupted or cannot be read. Please ensure file is valid Excel format.'
      }
    }
  } catch (error) {
    return {
      isValid: false,
      error: `Cannot read file: ${error.message}`
    }
  }
}

// Excel structure validation
function validateExcelStructure(sheetData) {
  if (!sheetData || !Array.isArray(sheetData) || sheetData.length === 0) {
    return {
      isValid: false,
      error: 'Sheet has no data rows'
    }
  }

  const firstRow = sheetData[0]
  if (!firstRow) {
    return {
      isValid: false,
      error: 'Excel sheet appears empty'
    }
  }

  const headers = Object.keys(firstRow)
  const requiredColumns = ['Full Names', 'Email', 'Result']
  
  const missingColumns = requiredColumns.filter(col => 
    !headers.some(header => header && header.toLowerCase().includes(col.toLowerCase()))
  )

  if (missingColumns.length > 0) {
    return {
      isValid: false,
      error: `Missing required columns: ${missingColumns.join(', ')}. Found: ${headers.slice(0, 5).join(', ')}`
    }
  }

  console.log(`✓ Validated sheet structure - Columns: ${headers.slice(0, 5).join(', ')}... - Rows: ${sheetData.length}`)
  return {
    isValid: true,
    columnCount: headers.length,
    rowCount: sheetData.length
  }
}

// Batch structure validation
function validateBatchStructure(fileArray) {
  if (!Array.isArray(fileArray)) {
    return {
      isValid: false,
      error: 'File array is invalid'
    }
  }

  if (fileArray.length !== 5) {
    return {
      isValid: false,
      error: `Need exactly 5 test files. Received ${fileArray.length} file(s).`
    }
  }

  // Verify all files exist and are Excel format
  const missingFiles = []
  fileArray.forEach(filePath => {
    if (!fs.existsSync(filePath)) {
      missingFiles.push(path.basename(filePath))
    }
  })

  if (missingFiles.length > 0) {
    return {
      isValid: false,
      error: `Files not found: ${missingFiles.join(', ')}`
    }
  }

  console.log(`✓ Batch structure validated - 5 files ready for processing`)
  return {
    isValid: true,
    fileCount: 5
  }
}

module.exports = {
  validateExcelFile,
  validateExcelStructure,
  validateBatchStructure
}
