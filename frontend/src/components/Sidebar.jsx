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
        <span className="material-icons-outlined" style={{fontSize: '20px'}}>{isOpen ? 'chevron_left' : 'chevron_right'}</span>
      </button>
      
      {isOpen && (
        <div className="sidebar-content">
          <div className="sidebar-section">
            <button
              onClick={async () => {
                if (!confirm('Delete ALL data (uploaded files, synced files, graphs, embeddings)? This cannot be undone!')) return
                try {
                  await filesAPI.deleteAllData()
                  alert('All data deleted successfully')
                  fetchFiles()
                  onFileSelect(null)
                } catch (error) {
                  alert('Failed to delete data: ' + error.message)
                }
              }}
              style={{
                width: '100%',
                padding: '8px',
                marginBottom: '15px',
                background: 'transparent',
                color: '#e5e7eb',
                border: '1px solid #6b7280',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = '#6b7280'
                e.target.style.color = 'white'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'transparent'
                e.target.style.color = '#e5e7eb'
              }}
            >
              <span className="material-icons-outlined" style={{fontSize: '18px', verticalAlign: 'middle', marginRight: '4px'}}>delete_sweep</span>Clear All Data
            </button>
          </div>

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
                    <span onClick={() => onFileSelect(file)}><span className="material-icons-outlined" style={{fontSize: '18px', verticalAlign: 'middle', marginRight: '8px'}}>description</span>{file.filename}</span>
                    <button 
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(file.file_id)
                      }}
                      title="Delete file"
                    >
                      <span className="material-icons-outlined" style={{fontSize: '16px'}}>delete</span>
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>

          <div className="sidebar-section">
            <h3>Synced Files</h3>
            {files.synced.length > 0 && (
              <button 
                className="process-all-btn"
                onClick={async () => {
                  try {
                    const { data } = await syncAPI.processAllSynced()
                    alert(data.message)
                    fetchFiles()
                  } catch (error) {
                    alert('Failed to process files: ' + error.message)
                  }
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginBottom: '12px',
                  background: 'transparent',
                  color: '#e5e7eb',
                  border: '1px solid #8b7355',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#8b7355'
                  e.target.style.color = 'white'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'transparent'
                  e.target.style.color = '#e5e7eb'
                }}
              >
                <span className="material-icons-outlined" style={{fontSize: '18px'}}>play_arrow</span>Process All
              </button>
            )}
            <ul className="file-list">
              {files.synced.length === 0 ? (
                <li className="empty">No synced files</li>
              ) : (
                files.synced.map((file, idx) => (
                  <li 
                    key={idx} 
                    className={`synced-file ${selectedFile?.file_id === file.file_id ? 'selected' : ''}`}
                    style={{ opacity: file.processed ? 1 : 0.6 }}
                  >
                    <span onClick={() => onFileSelect(file)} style={{display: 'flex', alignItems: 'center'}}><span className="material-icons-outlined" style={{fontSize: '18px', marginRight: '8px'}}>cloud</span><span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{file.filename}</span></span>
                    <div style={{display: 'flex', gap: '4px', flexShrink: 0}}>
                      <button 
                        className="process-btn"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleProcess(file.file_id)
                        }}
                        title={file.processed ? 'Reprocess file' : 'Process file'}
                      >
                        <span className="material-icons-outlined" style={{fontSize: '16px'}}>sync</span>
                      </button>
                      <button 
                        className="delete-btn"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(file.file_id)
                        }}
                        title="Delete file"
                      >
                        <span className="material-icons-outlined" style={{fontSize: '16px'}}>delete</span>
                      </button>
                    </div>
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
