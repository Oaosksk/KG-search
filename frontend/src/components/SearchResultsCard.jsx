import './SearchResultsCard.css'

export default function SearchResultsCard({ allResults }) {
  if (!allResults || allResults.length === 0) return null

  return (
    <div className="search-results-card">
      <h3>📊 Search Results</h3>
      <div className="results-scroll-container">
        {allResults.map((resultSet, setIdx) => (
          <div key={setIdx} className="result-set">
            {resultSet.results && resultSet.results.map((result, idx) => (
              <div key={idx} className="result-item">
                <div className="result-header">
                  <span className="result-number">• {idx + 1}</span>
                  <span className="result-source">{result.source}</span>
                </div>
                <p className="result-content">{result.content.substring(0, 150)}...</p>
                <div className="result-meta">
                  <span className="result-score">Score: {result.score.toFixed(3)}</span>
                </div>
              </div>
            ))}
            {setIdx < allResults.length - 1 && <div className="result-divider"></div>}
          </div>
        ))}
      </div>
    </div>
  )
}
