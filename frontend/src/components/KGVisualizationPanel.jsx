import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import './KGVisualizationPanel.css'

export default function KGVisualizationPanel({ data, viewMode }) {
  const svgRef = useRef()
  const [isMaximized, setIsMaximized] = useState(false)

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized)
  }

  useEffect(() => {
    if (!data || !data.nodes || data.nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight || 600

    // Add subtle shadow
    const defs = svg.append('defs')
    
    const filter = defs.append('filter').attr('id', 'shadow')
    filter.append('feGaussianBlur').attr('stdDeviation', '2').attr('result', 'blur')
    filter.append('feOffset').attr('in', 'blur').attr('dx', '0').attr('dy', '2').attr('result', 'offsetBlur')
    const feMerge = filter.append('feMerge')
    feMerge.append('feMergeNode').attr('in', 'offsetBlur')
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

    const zoom = d3.zoom()
      .scaleExtent([0.3, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    const g = svg.append('g')

    const nodes = data.nodes.map((n, i) => ({ id: i, ...n }))
    const links = data.edges || []

    function boxForce() {
      const padding = 80
      for (let node of nodes) {
        node.x = Math.max(padding, Math.min(width - padding, node.x))
        node.y = Math.max(padding, Math.min(height - padding, node.y))
      }
    }

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-800))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(60))
      .force('box', boxForce)

    // Links with subtle styling
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#475569')
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.25)
      .attr('stroke-linecap', 'round')

    // Node groups
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    // Main circle
    nodeGroup.append('circle')
      .attr('r', 18)
      .attr('fill', d => getNodeColor(d.entity_type))
      .attr('stroke', '#1e293b')
      .attr('stroke-width', 2)
      .style('filter', 'url(#shadow)')
      .style('cursor', 'pointer')
      .attr('opacity', 0.9)
      .on('mouseenter', function() {
        d3.select(this).transition().duration(150).attr('r', 22).attr('opacity', 1)
      })
      .on('mouseleave', function() {
        d3.select(this).transition().duration(150).attr('r', 18).attr('opacity', 0.9)
      })
      .on('click', (event, d) => {
        alert(`Entity: ${d.entity_text}\nType: ${d.entity_type}`)
      })

    // Labels with background
    const labelGroup = nodeGroup.append('g')
      .attr('transform', 'translate(0, -28)')

    labelGroup.append('rect')
      .attr('x', d => -(d.entity_text.length * 3.5 + 5))
      .attr('y', -9)
      .attr('width', d => d.entity_text.length * 7 + 10)
      .attr('height', 18)
      .attr('fill', 'rgba(15,23,42,0.85)')
      .attr('rx', 3)

    labelGroup.append('text')
      .text(d => d.entity_text.length > 15 ? d.entity_text.substring(0, 15) + '...' : d.entity_text)
      .attr('font-size', 10)
      .attr('font-weight', 500)
      .attr('fill', '#e2e8f0')
      .attr('text-anchor', 'middle')
      .attr('dy', 3)

    simulation.on('tick', () => {
      // Constrain nodes within bounds with padding for labels
      nodes.forEach(d => {
        d.x = Math.max(100, Math.min(width - 100, d.x))
        d.y = Math.max(60, Math.min(height - 60, d.y))
      })

      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      nodeGroup.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      event.subject.fx = event.subject.x
      event.subject.fy = event.subject.y
    }

    function dragged(event) {
      event.subject.fx = event.x
      event.subject.fy = event.y
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0)
      event.subject.fx = null
      event.subject.fy = null
    }

    function getNodeColor(type) {
      const colors = {
        'PERSON': '#60a5fa',
        'ORG': '#34d399',
        'DATE': '#818cf8',
        'MONEY': '#a78bfa',
        'GPE': '#22d3ee',
        'CARDINAL': '#fb923c',
        'PRODUCT': '#f472b6',
        'EVENT': '#fbbf24',
        'LOC': '#2dd4bf',
        'TIME': '#fb7185'
      }
      return colors[type] || '#818cf8'
    }

    return () => {
      simulation.stop()
    }

  }, [data])

  return (
    <div className={`kg-visualization-panel ${isMaximized ? 'maximized' : ''}`}>
      <div className="kg-header">
        <h2>Knowledge Graph {viewMode === 'combined' ? '(Combined View)' : '(Individual View)'}</h2>
        <button className="maximize-btn" onClick={toggleMaximize} title={isMaximized ? 'Minimize' : 'Maximize'}>
          {isMaximized ? '⊟' : '⊞'}
        </button>
      </div>
      {(!data || !data.nodes || data.nodes.length === 0) ? (
        <div className="kg-empty-state">
        
          <p>No knowledge graph data available</p>
          <p style={{ fontSize: '0.85rem', marginTop: '0.5rem', color: '#94a3b8' }}>
            {viewMode === 'individual' 
              ? 'This file has no processed data. Click the ⚙️ button to process it.'
              : 'Upload a file or perform a search to see entities'}
          </p>
        </div>
      ) : (
        <svg ref={svgRef} width="100%" height="100%"></svg>
      )}
    </div>
  )
}
