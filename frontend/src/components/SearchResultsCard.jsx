import { useState } from 'react'
import './SearchResultsCard.css'

export default function SearchResultsCard({ allResults }) {
  const [isMaximized, setIsMaximized] = useState(false)
  
  if (!allResults || allResults.length === 0) return null

  return (
    <div className={`search-results-card ${isMaximized ? 'maximized' : ''}`}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3><span className="material-icons-outlined" style={{fontSize: '20px', verticalAlign: 'middle', marginRight: '8px'}}>search</span>Search Results</h3>
        <button 
          onClick={() => setIsMaximized(!isMaximized)}
          className="maximize-btn"
          title={isMaximized ? 'Minimize' : 'Maximize'}
        >
          {isMaximized ? '⊟' : '⊞'}
        </button>
      </div>
      <div className="results-scroll-container">
        {allResults.map((resultSet, setIdx) => (
          <div key={setIdx} className="result-set">
            {resultSet.answer && (
              <div className="answer-display" >
                <strong>Answer:</strong> {resultSet.answer}
              </div>
            )}
            {false && resultSet.results && resultSet.results.map((result, idx) => {
              // Format content based on source
              let displayContent = result.content
              if (result.source === 'kg' && typeof result.content === 'string' && result.content.includes("'entity_text'")) {
                // Parse KG entity
                try {
                  const match = result.content.match(/'entity_text':\s*'([^']+)'.*'entity_type':\s*'([^']+)'/)
                  if (match) {
                    displayContent = `${match[1]} (${match[2]})`
                  }
                } catch (e) {
                  displayContent = result.content.substring(0, 100)
                }
              } else {
                displayContent = result.content.substring(0, 150)
              }
              
              return (
                <div key={idx} className="result-item">
                  <div className="result-header">
                    <span className="result-number">• {idx + 1}</span>
                    <span className="result-source"><span className="material-icons-outlined" style={{fontSize: '14px', verticalAlign: 'middle', marginRight: '4px'}}>{result.source === 'kg' ? 'account_tree' : result.source === 'vector' ? 'analytics' : 'search'}</span>{result.source === 'kg' ? 'KG' : result.source === 'vector' ? 'Vector' : 'BM25'}</span>
                  </div>
                  <p className="result-content">{displayContent}{displayContent.length < result.content.length ? '...' : ''}</p>
                  <div className="result-meta">
                    <span className="result-score">Score: {result.score.toFixed(3)}</span>
                  </div>
                </div>
              )
            })}
            {setIdx < allResults.length - 1 && <div className="result-divider"></div>}
          </div>
        ))}
      </div>
    </div>
  )
}
