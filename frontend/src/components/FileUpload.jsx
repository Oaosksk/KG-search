import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { uploadAPI } from '../services/api'
import './FileUpload.css'

export default function FileUpload() {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [stage, setStage] = useState('')

  const onDrop = useCallback(async (files) => {
    setUploading(true)
    
    try {
      for (const file of files) {
        setStage('processing')
        setMessage(`⚙️ Processing ${file.name} (parsing, building KG, generating embeddings)...`)
        await uploadAPI.uploadFile(file)
      }
      setStage('complete')
      setMessage('✅ Upload complete!')
      window.dispatchEvent(new Event('fileUploaded'))
      setTimeout(() => {
        setMessage('')
        setStage('')
      }, 3000)
    } catch (error) {
      setStage('error')
      setMessage('❌ Upload failed: ' + error.message)
      setTimeout(() => {
        setMessage('')
        setStage('')
      }, 5000)
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  return (
    <div className="file-upload">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'disabled' : ''}`}>
        <input {...getInputProps()} disabled={uploading} />
        <p>{uploading ? 'Processing...' : 'Drag files or click to upload'}</p>
        <small>CSV, XLSX, DOCX, PDF, JSON, TXT</small>
      </div>
      {message && (
        <div className={`message ${stage}`}>
          {uploading && <span className="spinner"></span>}
          {message}
        </div>
      )}
    </div>
  )
}
