// Request logging middleware
function requestLogger(req, res, next) {
  const start = Date.now()
  
  // Log request
  console.log(`\n→ ${new Date().toISOString()} | ${req.method} ${req.path}`)
  if (Object.keys(req.query).length > 0) {
    console.log(`  Query: ${JSON.stringify(req.query)}`)
  }

  // Hook response to log it
  const originalSend = res.send
  res.send = function(data) {
    const duration = Date.now() - start
    console.log(`← ${res.statusCode} | ${duration}ms`)
    return originalSend.call(this, data)
  }

  next()
}

module.exports = requestLogger
