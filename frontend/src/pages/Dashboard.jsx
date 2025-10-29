import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { filesAPI } from '../services/api'
import ChatSearchInterface from '../components/ChatSearchInterface'
import SearchResultsCard from '../components/SearchResultsCard'
import Sidebar from '../components/Sidebar'
import GDriveSync from '../components/GDriveSync'
import ThemeToggle from '../components/ThemeToggle'
import KGVisualizationPanel from '../components/KGVisualizationPanel'
import './Dashboard.css'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [searchResults, setSearchResults] = useState(null)
  const [allResults, setAllResults] = useState([])
  const [viewMode, setViewMode] = useState('individual')
  const [selectedFile, setSelectedFile] = useState(null)
  const [kgData, setKgData] = useState({ nodes: [], edges: [] })

  const handleFileSelect = async (file) => {
    setSelectedFile(file)
    
    // Fetch KG for selected file in individual mode
    if (viewMode === 'individual' && file?.file_id) {
      try {
        const { data } = await filesAPI.getFileKG(file.file_id)
        setKgData(data)
      } catch (error) {
        console.error('Failed to fetch file KG:', error)
      }
    }
  }

  const handleNewResults = (data) => {
    setSearchResults(data)
    setAllResults(prev => [...prev, data])
    
    // Update KG visualization with data from search (combined mode)
    if (viewMode === 'combined') {
      if (data.kg_data) {
        setKgData(data.kg_data)
      } else if (data.kg_entities && data.kg_entities.length > 0) {
        setKgData({ nodes: data.kg_entities, edges: [] })
      }
    }
  }

  const handleViewModeChange = async (mode) => {
    setViewMode(mode)
    
    // If switching to individual mode and file is selected, fetch its KG
    if (mode === 'individual' && selectedFile?.file_id) {
      try {
        const { data } = await filesAPI.getFileKG(selectedFile.file_id)
        setKgData(data)
      } catch (error) {
        console.error('Failed to fetch file KG:', error)
      }
    }
  }

  const handleFirstFileLoaded = async (firstFile) => {
    if (firstFile && viewMode === 'individual') {
      setSelectedFile(firstFile)
      try {
        const { data } = await filesAPI.getFileKG(firstFile.file_id)
        setKgData(data)
      } catch (error) {
        console.error('Failed to fetch first file KG:', error)
      }
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>KG-Search</h1>
        <div className="header-actions">
          <GDriveSync />
          <ThemeToggle />
          <div className="user-info">
            <img src={user?.picture} alt={user?.name} />
            <span>{user?.name}</span>
            <button onClick={logout}>Logout</button>
          </div>
        </div>
      </header>
      
      <div className="dashboard-body">
        <Sidebar 
          onFileSelect={handleFileSelect}
          viewMode={viewMode}
          onViewModeChange={handleViewModeChange}
          onFirstFileLoaded={handleFirstFileLoaded}
          selectedFile={selectedFile}
        />
        
        <div className="dashboard-main">
          <div className="dashboard-content-wrapper">
            <div className="search-input-section">
              <ChatSearchInterface 
                onResults={setSearchResults} 
                onAllResults={handleNewResults}
              />
            </div>
            
            <div className="results-section">
              {allResults.length > 0 ? (
                <SearchResultsCard allResults={allResults} />
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#999' }}>
                  <p>Search results will appear here</p>
                </div>
              )}
            </div>
            
            <div className="kg-section">
              <KGVisualizationPanel data={kgData} viewMode={viewMode} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
