const XLSX = require('xlsx')
const path = require('path')
const fs = require('fs')

// Read Excel file and extract data
function readExcelFile(filePath) {
  try {
    const workbook = XLSX.readFile(filePath)
    const sheetName = workbook.SheetNames[0] // Use first sheet
    const sheet = workbook.Sheets[sheetName]
    
    // Convert sheet to array of objects
    const data = XLSX.utils.sheet_to_json(sheet)
    
    console.log(`✓ Read Excel file: ${path.basename(filePath)} - ${data.length} rows`)
    return data
  } catch (error) {
    throw new Error(`Failed to read Excel file: ${error.message}`)
  }
}

// Create merge key from name
function createMergeKey(fullName) {
  if (!fullName) return ''
  return fullName
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ') // Normalize whitespace
}

// Merge test results from all 5 files
function mergeTestResults(test1Data, test2Data, test3Data, test4Data, test5Data) {
  const mergedMap = new Map()

  // Process each test file
  const testFiles = [
    { data: test1Data, testNum: 1 },
    { data: test2Data, testNum: 2 },
    { data: test3Data, testNum: 3 },
    { data: test4Data, testNum: 4 },
    { data: test5Data, testNum: 5 }
  ]

  testFiles.forEach(({ data, testNum }) => {
    data.forEach(row => {
      const key = createMergeKey(row['Full Names'])
      
      if (!mergedMap.has(key)) {
        mergedMap.set(key, {
          'Full Names': row['Full Names'],
          'Email': row['Email'],
          'TEST_1': null,
          'TEST_2': null,
          'TEST_3': null,
          'TEST_4': null,
          'TEST_5': null
        })
      }

      const record = mergedMap.get(key)
      const resultValue = parseFloat(row['Result']) || 0
      record[`TEST_${testNum}`] = resultValue
    })
  })

  const merged = Array.from(mergedMap.values())
  console.log(`✓ Merged test results - ${merged.length} participants`)
  return merged
}

// Calculate scores
function calculateScores(mergedData) {
  return mergedData.map(record => {
    const test1 = parseFloat(record['TEST_1']) || 0
    const test2 = parseFloat(record['TEST_2']) || 0
    const test3 = parseFloat(record['TEST_3']) || 0
    const test4 = parseFloat(record['TEST_4']) || 0
    const test5 = parseFloat(record['TEST_5']) || 0

    // Calculate total
    const total = test1 + test2 + test3 + test4 + test5

    // Apply formula: (TOTAL + 0.8) × 16.6666
    const score = (total + 0.8) * 16.6666
    
    // Determine status
    const status = score >= 50 ? 'PASS' : 'FAIL'

    return {
      ...record,
      'SCORE': Math.round(score * 100) / 100, // Round to 2 decimal places
      'STATUS': status
    }
  })
}

// Generate result Excel file
function generateResultFile(processedData, outputPath) {
  try {
    // Define columns in specific order
    const columns = [
      'S/N',
      'Full Names',
      'Email',
      'TEST_1',
      'TEST_2',
      'TEST_3',
      'TEST_4',
      'TEST_5',
      'SCORE',
      'STATUS'
    ]

    // Prepare data with S/N
    const dataWithSN = processedData.map((record, index) => ({
      'S/N': index + 1,
      'Full Names': record['Full Names'],
      'Email': record['Email'],
      'TEST_1': record['TEST_1'],
      'TEST_2': record['TEST_2'],
      'TEST_3': record['TEST_3'],
      'TEST_4': record['TEST_4'],
      'TEST_5': record['TEST_5'],
      'SCORE': record['SCORE'],
      'STATUS': record['STATUS']
    }))

    // Create workbook and sheet
    const workbook = XLSX.utils.book_new()
    const worksheet = XLSX.utils.json_to_sheet(dataWithSN)

    // Set column widths
    worksheet['!cols'] = [
      { wch: 5 },   // S/N
      { wch: 25 },  // Full Names
      { wch: 25 },  // Email
      { wch: 10 },  // TEST_1
      { wch: 10 },  // TEST_2
      { wch: 10 },  // TEST_3
      { wch: 10 },  // TEST_4
      { wch: 10 },  // TEST_5
      { wch: 10 },  // SCORE
      { wch: 10 }   // STATUS
    ]

    // Add sheet to workbook
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Results')

    // Write file
    XLSX.writeFile(workbook, outputPath)
    
    console.log(`✓ Generated result file: ${path.basename(outputPath)}`)
    return outputPath
  } catch (error) {
    throw new Error(`Failed to generate result file: ${error.message}`)
  }
}

// Main processing function
async function processCompleteJob(filePathArray) {
  try {
    // Validate we have exactly 5 files
    if (filePathArray.length !== 5) {
      throw new Error(`Expected 5 files, got ${filePathArray.length}`)
    }

    console.log('📋 Starting Excel processing...')

    // Read all files
    console.log('1️⃣  Reading Excel files...')
    const test1Data = readExcelFile(filePathArray[0])
    const test2Data = readExcelFile(filePathArray[1])
    const test3Data = readExcelFile(filePathArray[2])
    const test4Data = readExcelFile(filePathArray[3])
    const test5Data = readExcelFile(filePathArray[4])

    // Merge data
    console.log('2️⃣  Merging test results...')
    const mergedData = mergeTestResults(test1Data, test2Data, test3Data, test4Data, test5Data)

    // Calculate scores
    console.log('3️⃣  Calculating scores...')
    const processedData = calculateScores(mergedData)

    // Calculate statistics
    const passCount = processedData.filter(r => r.STATUS === 'PASS').length
    const failCount = processedData.filter(r => r.STATUS === 'FAIL').length

    // Generate output file
    console.log('4️⃣  Generating output file...')
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0]
    const outputPath = path.join(__dirname, '../../uploads', `Results_${timestamp}.xlsx`)
    generateResultFile(processedData, outputPath)

    console.log(`✅ Processing complete - ${processedData.length} participants, ${passCount} PASS, ${failCount} FAIL`)

    return {
      success: true,
      resultFile: outputPath,
      participantCount: processedData.length,
      passCount,
      failCount,
      timestamp: new Date().toISOString()
    }
  } catch (error) {
    console.error('❌ Processing error:', error.message)
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    }
  }
}

module.exports = {
  readExcelFile,
  createMergeKey,
  mergeTestResults,
  calculateScores,
  generateResultFile,
  processCompleteJob
}
