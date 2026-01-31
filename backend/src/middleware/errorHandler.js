// Global error handler middleware
function errorHandler(err, req, res, next) {
  console.error('🔴 ERROR:', err.message)
  console.error('   Stack:', err.stack)

  // Default error response
  const statusCode = err.statusCode || 500
  const message = err.message || 'Internal server error'

  res.status(statusCode).json({
    error: true,
    message: message,
    status: statusCode,
    timestamp: new Date().toISOString()
  })
}

module.exports = errorHandler
