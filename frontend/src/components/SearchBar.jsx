import { useState, useRef } from 'react'
import { searchAPI, uploadAPI } from '../services/api'
import './SearchBar.css'

export default function SearchBar({ onResults }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef()

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      const { data } = await searchAPI.search(query)
      onResults(data)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setLoading(true)
    try {
      await uploadAPI.uploadFile(file)
      alert('File uploaded successfully!')
    } catch (error) {
      alert('Upload failed: ' + error.message)
    } finally {
      setLoading(false)
      e.target.value = ''
    }
  }

  return (
    <form onSubmit={handleSearch} className="search-bar">
      <button 
        type="button" 
        className="upload-btn"
        onClick={() => fileInputRef.current.click()}
        disabled={loading}
      >
        +
      </button>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        style={{ display: 'none' }}
        accept=".csv,.xlsx,.docx,.pdf,.json,.txt"
      />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
    </form>
  )
}
