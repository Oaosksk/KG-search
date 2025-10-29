import { useState, useEffect } from 'react'
import { filesAPI, syncAPI } from '../services/api'
import './Sidebar.css'

export default function Sidebar({ onFileSelect, viewMode, onViewModeChange, onFirstFileLoaded, selectedFile }) {
  const [isOpen, setIsOpen] = useState(true)
  const [files, setFiles] = useState({ uploaded: [], synced: [] })

  useEffect(() => {
    fetchFiles()
    
    const handleFileUpload = () => fetchFiles()
    const handleSync = () => fetchFiles()
    
    window.addEventListener('fileUploaded', handleFileUpload)
    window.addEventListener('driveSync', handleSync)
    
    return () => {
      window.removeEventListener('fileUploaded', handleFileUpload)
      window.removeEventListener('driveSync', handleSync)
    }
  }, [])

  useEffect(() => {
    // Auto-select first file when files are loaded
    if (files.uploaded.length > 0 && !selectedFile && onFirstFileLoaded) {
      onFirstFileLoaded(files.uploaded[0])
    }
  }, [files.uploaded])

  useEffect(() => {
    const sidebar = document.querySelector('.sidebar')
    const main = document.querySelector('.dashboard-main')
    
    if (sidebar && main) {
      if (isOpen) {
        sidebar.classList.remove('closed')
        sidebar.classList.add('open')
      } else {
        sidebar.classList.remove('open')
        sidebar.classList.add('closed')
      }
    }
  }, [isOpen])

  const fetchFiles = async () => {
    try {
      const { data } = await filesAPI.listFiles()
      setFiles(data)
    } catch (error) {
      console.error('Failed to fetch files:', error)
    }
  }

  const handleDelete = async (fileId) => {
    if (!confirm('Delete this file and all its data?')) return
    
    try {
      await filesAPI.deleteFile(fileId)
      fetchFiles()
      if (selectedFile?.file_id === fileId) {
        onFileSelect(null)
      }
    } catch (error) {
      console.error('Failed to delete file:', error)
      alert('Failed to delete file')
    }
  }

  const handleProcess = async (fileId) => {
    try {
      await syncAPI.processGDriveFile(fileId)
      alert('File processing started!')
      fetchFiles()
    } catch (error) {
      console.error('Failed to process file:', error)
      alert('Failed to process file')
    }
  }

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <button className="sidebar-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '◀' : '▶'}
      </button>
      
      {isOpen && (
        <div className="sidebar-content">
          <div className="sidebar-section">
            <h3>View Mode</h3>
            <div className="view-mode-buttons">
              <button 
                className={viewMode === 'individual' ? 'active' : ''}
                onClick={() => onViewModeChange('individual')}
              >
                Individual
              </button>
              <button 
                className={viewMode === 'combined' ? 'active' : ''}
                onClick={() => onViewModeChange('combined')}
              >
                Combined
              </button>
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Uploaded Files</h3>
            <ul className="file-list">
              {files.uploaded.length === 0 ? (
                <li className="empty">No files uploaded</li>
              ) : (
                files.uploaded.map((file, idx) => (
                  <li 
                    key={idx} 
                    className={selectedFile?.file_id === file.file_id ? 'selected' : ''}
                  >
                    <span onClick={() => onFileSelect(file)}>📄 {file.filename}</span>
                    <button 
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(file.file_id)
                      }}
                      title="Delete file"
                    >
                      🗑️
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>

          <div className="sidebar-section">
            <h3>Synced Files</h3>
            <ul className="file-list">
              {files.synced.length === 0 ? (
                <li className="empty">No synced files</li>
              ) : (
                files.synced.map((file, idx) => (
                  <li 
                    key={idx} 
                    className={`synced-file ${selectedFile?.file_id === file.file_id ? 'selected' : ''}`}
                  >
                    <span onClick={() => onFileSelect(file)}>☁️ {file.filename}</span>
                    <button 
                      className="process-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleProcess(file.file_id)
                      }}
                      title="Download and process file"
                    >
                      ⚙️
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
