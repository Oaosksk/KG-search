import { useState, useEffect } from 'react'
import { syncAPI } from '../services/api'
import './GDriveSync.css'

export default function GDriveSync() {
  const [syncing, setSyncing] = useState(false)
  const [synced, setSynced] = useState(false)
  const [enabled, setEnabled] = useState(false)

  useEffect(() => {
    // Clear old sync state to force fresh sync
    localStorage.removeItem('gdrive_sync_enabled')
  }, [])

  const handleToggle = async () => {
    if (enabled) {
      setEnabled(false)
      setSynced(false)
      localStorage.removeItem('gdrive_sync_enabled')
      window.dispatchEvent(new CustomEvent('driveSync'))
      return
    }

    setSyncing(true)
    try {
      const { data } = await syncAPI.syncGoogleDrive()
      setSynced(true)
      setEnabled(true)
      
      window.dispatchEvent(new CustomEvent('driveSync', { detail: data }))
      
      setTimeout(() => setSyncing(false), 1000)
    } catch (error) {
      console.error('Sync failed:', error)
      const errorMsg = error.response?.data?.detail || error.message
      
      if (error.response?.status === 401 || errorMsg.includes('authentication')) {
        alert('Google Drive authentication expired. Please log out and log in again to grant Drive permissions.')
      } else {
        alert('Sync failed: ' + errorMsg)
      }
      
      setSyncing(false)
      setEnabled(false)
    }
  }

  return (
    <div className="gdrive-sync">
      <label className="sync-label">
        <span>Google Drive Sync</span>
        <div className="toggle-wrapper">
          <input
            type="checkbox"
            checked={enabled}
            onChange={handleToggle}
            disabled={syncing}
          />
          <span className="toggle-slider"></span>
        </div>
      </label>
      
      {syncing && (
        <span className="sync-status syncing">
          <span className="spinner"></span> Syncing...
        </span>
      )}
      
      {synced && !syncing && (
        <span className="sync-status synced">
          ✓ Synced
        </span>
      )}
    </div>
  )
}
