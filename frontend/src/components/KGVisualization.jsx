import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import './KGVisualization.css'

export default function KGVisualization({ entities }) {
  const svgRef = useRef()

  useEffect(() => {
    if (!entities || entities.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 800
    const height = 400

    const nodes = entities.map((e, i) => ({ id: i, ...e }))
    const links = []
    for (let i = 0; i < nodes.length - 1; i++) {
      links.push({ source: i, target: i + 1 })
    }

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))

    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 2)

    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', 20)
      .attr('fill', '#667eea')

    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text(d => d.entity_text)
      .attr('font-size', 12)
      .attr('dx', 25)

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y)
    })
  }, [entities])

  if (!entities || entities.length === 0) return null

  return (
    <div className="kg-visualization">
      <h3>Knowledge Graph</h3>
      <svg ref={svgRef} width="800" height="800"></svg>
    </div>
  )
}
