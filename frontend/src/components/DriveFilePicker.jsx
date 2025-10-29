import { useState } from 'react'
import { uploadAPI } from '../services/api'
import './DriveFilePicker.css'

export default function DriveFilePicker() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleDrivePicker = async () => {
    setLoading(true)
    setMessage('')
    
    try {
      const token = localStorage.getItem('token')
      // This would open Google Drive picker
      // For now, just show message
      setMessage('Google Drive integration - coming soon!')
    } catch (error) {
      setMessage('Failed to access Drive: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="drive-picker">
      <button onClick={handleDrivePicker} disabled={loading}>
        {loading ? 'Loading...' : '📁 Import from Google Drive'}
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  )
}
