import { useEffect, useState } from 'react'
import api from '../api'

function ProcessingModal({ moduleId, onComplete }) {
  const [status, setStatus] = useState({
    processing_status: 'pending',
    processing_step: 'Starting...',
    processing_progress: 0
  })

  useEffect(() => {
    if (!moduleId) return

    const pollStatus = async () => {
      try {
        const response = await api.get(`/modules/${moduleId}/status`)
        setStatus(response.data)

        if (response.data.processing_status === 'completed') {
          setTimeout(() => {
            onComplete()
          }, 2000)
        } else if (response.data.processing_status === 'error') {
          setTimeout(() => {
            onComplete()
          }, 3000)
        }
      } catch (error) {
        console.error('Error fetching status:', error)
      }
    }

    // Poll every 500ms for faster updates
    const interval = setInterval(pollStatus, 500)
    pollStatus() // Initial call

    return () => clearInterval(interval)
  }, [moduleId, onComplete])

  const getStatusColor = () => {
    switch (status.processing_status) {
      case 'completed':
        return 'text-success'
      case 'error':
        return 'text-error'
      case 'processing':
        return 'text-primary'
      default:
        return 'text-base-content'
    }
  }

  const getStatusIcon = () => {
    switch (status.processing_status) {
      case 'completed':
        return '✅'
      case 'error':
        return '❌'
      case 'processing':
        return '⚙️'
      default:
        return '⏳'
    }
  }

  return (
    <div className="modal modal-open">
      <div className="modal-box max-w-2xl">
        <h3 className="font-bold text-2xl mb-6 text-center">
          {getStatusIcon()} Processing Module
        </h3>

        <div className="space-y-6">
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm font-medium">{status.processing_progress}%</span>
            </div>
            <progress
              className="progress progress-primary w-full h-4"
              value={status.processing_progress}
              max="100"
            ></progress>
          </div>

          {/* Status Message */}
          <div className="card bg-base-200">
            <div className="card-body">
              <h4 className="font-semibold mb-2">Current Step:</h4>
              <p className={`text-lg ${getStatusColor()}`}>
                {status.processing_step}
              </p>
            </div>
          </div>


          {status.processing_status === 'completed' && (
            <div className="alert alert-success">
              <span>✅ Module created successfully! Redirecting...</span>
            </div>
          )}

          {status.processing_status === 'error' && (
            <div className="alert alert-error">
              <span>❌ An error occurred during processing. Please try again.</span>
            </div>
          )}
        </div>

        {(status.processing_status === 'completed' || status.processing_status === 'error') && (
          <div className="modal-action">
            <button onClick={onComplete} className="btn btn-primary">
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProcessingModal
