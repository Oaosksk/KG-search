import ReactMarkdown from 'react-markdown'
import { useState } from 'react'
import { searchAPI } from '../services/api'
import './SearchResults.css'

export default function SearchResults({ results }) {
  const [rating, setRating] = useState(0)

  const handleFeedback = async (r) => {
    setRating(r)
    await searchAPI.submitFeedback({
      query: results.query,
      answer: results.answer,
      rating: r
    })
  }

  return (
    <div className="search-results">
      <div className="answer-section">
        <h2>Answer</h2>
        <ReactMarkdown>{results.answer}</ReactMarkdown>
        
        <div className="feedback">
          <span>Rate this answer:</span>
          {[1,2,3,4,5].map(r => (
            <button key={r} onClick={() => handleFeedback(r)} className={rating === r ? 'active' : ''}>
              ⭐
            </button>
          ))}
        </div>
      </div>

      <div className="sources-section">
        <h3>Sources</h3>
        {results.results.map((result, idx) => (
          <div key={idx} className="source-card">
            <span className="citation">[{idx + 1}]</span>
            <p>{result.content.substring(0, 200)}...</p>
            <small>Score: {result.score.toFixed(3)}</small>
          </div>
        ))}
      </div>
    </div>
  )
}
