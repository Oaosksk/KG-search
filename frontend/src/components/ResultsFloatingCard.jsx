import { useState } from 'react'
import './ResultsFloatingCard.css'

export default function ResultsFloatingCard({ results }) {
  const [isExpanded, setIsExpanded] = useState(true)

  if (!results || !results.results || results.results.length === 0) return null

  return (
    <div className={`results-floating-card ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="card-header">
        <h3>📊 Search Results ({results.results.length})</h3>
        <button onClick={() => setIsExpanded(!isExpanded)} className="toggle-btn">
          {isExpanded ? '▼' : '▲'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="card-content">
          {results.results.map((result, idx) => (
            <div key={idx} className="result-item">
              <span className="result-badge">[{idx + 1}]</span>
              <div className="result-text">
                <p>{result.content.substring(0, 200)}...</p>
                <small>Score: {result.score.toFixed(3)} | Source: {result.source}</small>
              </div>
            </div>
          ))}
          
          {results.citations && results.citations.length > 0 && (
            <div className="citations">
              <h4>Citations:</h4>
              <ul>
                {results.citations.map((citation, idx) => (
                  <li key={idx}>[{idx + 1}] {citation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
