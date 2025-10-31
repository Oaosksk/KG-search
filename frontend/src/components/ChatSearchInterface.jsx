import { useState, useRef, useEffect } from 'react'
import { searchAPI, uploadAPI } from '../services/api'
import './ChatSearchInterface.css'

export default function ChatSearchInterface({ onResults, onAllResults }) {
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    const userMessage = { type: 'user', content: query, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setLoading(true)

    try {
      const { data } = await searchAPI.search(query)
      console.log('[SEARCH] API Response:', data)
      console.log('[SEARCH] Answer:', data.answer)
      console.log('[SEARCH] Results count:', data.results?.length)
      console.log('[SEARCH] KG entities count:', data.kg_entities?.length)
      
      const aiMessage = {
        type: 'ai',
        content: data.answer,
        results: data.results,
        kg_entities: data.kg_entities,
        citations: data.citations,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, aiMessage])
      onResults(data)
      onAllResults(data)
    } catch (error) {
      const errorMessage = {
        type: 'ai',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const uploadMessage = { type: 'user', content: `📎 ${file.name}`, timestamp: new Date() }
    setMessages(prev => [...prev, uploadMessage])

    const processingMessage = { type: 'ai', content: `⚙️ Processing file (parsing, building knowledge graph, generating embeddings)...`, timestamp: new Date(), processing: true }
    setMessages(prev => [...prev, processingMessage])
    setLoading(true)

    try {
      const response = await uploadAPI.uploadFile(file)
      setMessages(prev => prev.filter(m => !m.processing))
      const successMessage = { type: 'ai', content: `✅ File "${file.name}" processed successfully! You can now search it.`, timestamp: new Date() }
      setMessages(prev => [...prev, successMessage])
      
      window.dispatchEvent(new CustomEvent('fileUploaded', { detail: response.data }))
    } catch (error) {
      setMessages(prev => prev.filter(m => !m.processing))
      const errorMessage = { type: 'ai', content: `❌ Upload failed: ${error.response?.data?.detail || error.message}`, timestamp: new Date() }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      e.target.value = ''
    }
  }

  return (
    <div className="chat-search-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <h3>Welcome to KG-Search</h3>
            <p>Ask me anything about your documents</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            <div className="message-bubble">
              <p style={{whiteSpace: 'pre-wrap'}}>{msg.content}</p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message ai">
            <div className="message-bubble typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSearch} className="chat-input-form">
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
          className="chat-input"
        />
        <button type="submit" disabled={loading} className="send-btn">
          {loading ? '⏳' : '➤'}
        </button>
      </form>
    </div>
  )
}
