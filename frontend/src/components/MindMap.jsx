import { useCallback, useMemo, useState } from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'

function MindMap({ data, onInteract }) {
  const [selectedNode, setSelectedNode] = useState(null)
  if (!data || !data.central || !data.nodes) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Invalid Mind Map Data</h3>
              <div className="text-sm">This mind map is missing central concept or nodes.</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const { initialNodes, initialEdges } = useMemo(() => {
    const nodes = []
    const edges = []
    
    nodes.push({
      id: 'central',
      type: 'default',
      data: { 
        label: data.central,
        description: 'Central concept',
        fullData: data
      },
      position: { x: 400, y: 200 },
      style: { background: '#36d399', color: '#fff', border: '2px solid #2aa882', borderRadius: '20px', padding: '15px 25px', fontSize: '18px', fontWeight: 'bold', minWidth: '150px', textAlign: 'center' }
    })
    
    const radius = 250
    const primaryCount = data.nodes.length
    
    data.nodes.forEach((node, idx) => {
      const nodeLabel = typeof node === 'string' ? node : (node.title || node.label || 'Unnamed')
      const nodeChildren = typeof node === 'string' ? [] : (node.nodes || node.children || [])
      const angle = (2 * Math.PI * idx) / primaryCount - Math.PI / 2
      const x = 400 + radius * Math.cos(angle)
      const y = 200 + radius * Math.sin(angle)
      const primaryId = `primary-${idx}`
      
      nodes.push({
        id: primaryId,
        type: 'default',
        data: { 
          label: `${nodeLabel} ${nodeChildren.length > 0 ? `(${nodeChildren.length})` : ''}`,
          description: typeof node === 'object' ? node.description : null,
          fullData: node
        },
        position: { x, y },
        style: { background: '#3b82f6', color: '#fff', border: '2px solid #2563eb', borderRadius: '15px', padding: '10px 20px', fontSize: '14px', fontWeight: '600', minWidth: '120px', textAlign: 'center' }
      })
      
      edges.push({
        id: `edge-central-${primaryId}`,
        source: 'central',
        target: primaryId,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#3b82f6', strokeWidth: 2 }
      })
      
      if (nodeChildren && nodeChildren.length > 0) {
        const childRadius = 180
        const childCount = nodeChildren.length
        const angleSpread = Math.min(1.2, childCount * 0.4)
        
        nodeChildren.forEach((child, childIdx) => {
          const childLabel = typeof child === 'string' ? child : (child.title || child.label || 'Unnamed')
          const childAngle = angle + (childIdx - (childCount - 1) / 2) * (angleSpread / Math.max(1, childCount - 1))
          const childX = x + childRadius * Math.cos(childAngle)
          const childY = y + childRadius * Math.sin(childAngle)
          const childId = `child-${idx}-${childIdx}`
          
          nodes.push({
            id: childId,
            type: 'default',
            data: { 
              label: childLabel,
              description: typeof child === 'object' ? child.description : null,
              fullData: child
            },
            position: { x: childX, y: childY },
            style: { background: '#22d3ee', color: '#fff', border: '2px solid #06b6d4', borderRadius: '12px', padding: '8px 15px', fontSize: '12px', fontWeight: '500', minWidth: '100px', textAlign: 'center' }
          })
          
          edges.push({
            id: `edge-${primaryId}-${childId}`,
            source: primaryId,
            target: childId,
            type: 'smoothstep',
            style: { stroke: '#22d3ee', strokeWidth: 1.5 }
          })
        })
      }
    })
    
    return { initialNodes: nodes, initialEdges: edges }
  }, [data])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onNodeClick = useCallback((event, node) => {
    if (onInteract) onInteract()
    setSelectedNode(node)
  }, [onInteract])

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title text-2xl mb-4">Mind Map</h2>
        
        <div style={{ width: '100%', height: '600px' }} className="rounded-lg overflow-hidden border-2 border-base-300">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Controls />
            <MiniMap 
              nodeColor={(node) => {
                if (node.id === 'central') return '#36d399'
                if (node.id.startsWith('primary')) return '#3b82f6'
                return '#22d3ee'
              }}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
            <Background variant="dots" gap={12} size={1} />
          </ReactFlow>
        </div>
        
        {selectedNode && (
          <div className="mt-4 p-4 bg-base-200 rounded-lg border-2 border-primary">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-lg">{selectedNode.data.label}</h3>
              <button 
                onClick={() => setSelectedNode(null)}
                className="btn btn-ghost btn-xs btn-circle"
              >
                ✕
              </button>
            </div>
            {selectedNode.data.description && (
              <p className="text-sm mt-2">{selectedNode.data.description}</p>
            )}
            {selectedNode.id !== 'central' && (
              <div className="mt-2 text-xs text-gray-500">
                Click the ✕ to close this description
              </div>
            )}
          </div>
        )}
        
        {!selectedNode && (
          <p className="text-sm text-gray-500 mt-4 text-center">
            Click on any node to see details
          </p>
        )}
      </div>
    </div>
  )
}

export default MindMap
