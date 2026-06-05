"use client";

import { useState, useEffect, useCallback } from "react";
import {
  ReactFlow, Background, Controls, MiniMap, Node, Edge, useNodesState, useEdgesState,
  ConnectionLineType, Panel, Handle, Position, NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { motion } from "framer-motion";
import { Network, Search, ZoomIn, Loader2, ChevronRight, Link2 } from "lucide-react";
import { getSubgraph } from "@/lib/api";

function TorahNode({ data, selected }: NodeProps) {
  const d = data as any;
  const colors: Record<string, string> = {
    Book: "border-blue-500 bg-blue-50",
    Chapter: "border-indigo-500 bg-indigo-50",
    Verse: "border-purple-500 bg-purple-50",
    Person: "border-amber-500 bg-amber-50",
    TextChunk: "border-slate-500 bg-slate-50",
  };
  const color = colors[d.type] || "border-slate-500 bg-slate-50";

  return (
    <div
      className={`relative rounded-lg border-2 shadow-md transition-all ${color} ${
        selected ? "ring-4 ring-blue-400 shadow-xl scale-110" : "hover:shadow-lg hover:scale-105"
      }`}
      style={{ minWidth: d.type === "Verse" ? "120px" : "80px", maxWidth: "180px" }}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2" />
      <div className="px-3 py-2">
        <div className="text-[10px] font-bold uppercase text-slate-500">{d.type}</div>
        <div className="text-sm font-bold text-slate-900 truncate">{String(d.label || "")}</div>
        {d.hebrew && (
          <div className="text-xs text-slate-700 mt-1" dir="rtl">{String(d.hebrew).substring(0, 30)}</div>
        )}
        {d.role && <div className="text-[10px] text-slate-500">{String(d.role)}</div>}
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2" />
    </div>
  );
}

const nodeTypes = { torahNode: TorahNode };

function layoutNodes(nodes: any[], edges: any[]) {
  const centerX = 400;
  const centerY = 300;
  const levelHeight = 150;
  const angleStep = (2 * Math.PI) / Math.max(nodes.length - 1, 1);

  return nodes.map((n, i) => {
    const level = (n.depth || 0) + 1;
    const angle = i * angleStep;
    const radius = level * 200;
    return {
      ...n,
      position: {
        x: centerX + Math.cos(angle) * radius - (n.type === "Verse" ? 60 : 40),
        y: centerY + Math.sin(angle) * radius - 30,
      },
    };
  });
}

export function GraphExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [loading, setLoading] = useState(true);
  const [centerRef, setCenterRef] = useState("משה רבנו");
  const [depth, setDepth] = useState(2);

  const loadGraph = async (ref: string, d: number) => {
    setLoading(true);
    try {
      const data = await getSubgraph(ref, d, 150);
      const graphNodes = (data.nodes || []).map((n: any) => ({
        id: n.id || n.ref || String(Math.random()),
        type: "torahNode",
        position: { x: 0, y: 0 },
        data: { ...n, depth: n.depth || 0 },
      }));
      const graphEdges = (data.edges || []).map((e: any, i: number) => ({
        id: `e${i}`,
        source: e.from_id || e.source,
        target: e.to_id || e.target,
        label: e.type || "RELATED",
        type: "smoothstep",
        animated: e.type === "MENTIONS",
        style: { stroke: e.type === "MENTIONS" ? "#f59e0b" : "#94a3b8", strokeWidth: 1.5 },
      }));

      const positioned = layoutNodes(graphNodes, graphEdges);
      setNodes(positioned);
      setEdges(graphEdges);
    } catch (e) {
      console.error("Graph load failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph(centerRef, depth);
  }, [centerRef, depth]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
      setCenterRef(String((node.data as any)?.ref || node.id));
    },
    []
  );

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3 p-3 bg-white/5 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={centerRef}
            onChange={(e) => setCenterRef(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadGraph(centerRef, depth)}
            placeholder="הזן שם או פסוק..."
            className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white outline-none focus:ring-2 focus:ring-amber-500/50 w-48"
            dir="rtl"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">עומק:</span>
          <input
            type="range" min="1" max="5" value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
            className="w-20"
          />
          <span className="text-sm text-slate-400 w-4">{depth}</span>
        </div>
        <div className="flex-1" />
        <span className="text-sm text-slate-500">{nodes.length} צמתים | {edges.length} קשרים</span>
      </div>

      <div className="flex flex-1">
        <div className="flex-1 relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#0a0e1a]/80 z-10">
              <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
            </div>
          )}
          <ReactFlow
            nodes={nodes} edges={edges}
            onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView minZoom={0.1} maxZoom={2}
            connectionLineType={ConnectionLineType.SmoothStep}
          >
            <Background gap={16} />
            <Controls />
            <MiniMap
              nodeColor={(n) => {
                const colors: Record<string, string> = { Book: "#3b82f6", Chapter: "#6366f1", Verse: "#8b5cf6", Person: "#f59e0b", TextChunk: "#64748b" };
                return colors[(n.data as any)?.type] || "#999";
              }}
            />
            <Panel position="top-right" className="m-2">
              <div className="bg-[#0d1321]/95 p-3 rounded-lg shadow-lg border border-white/10 text-xs space-y-1">
                {Object.entries({ Book: "#3b82f6", Chapter: "#6366f1", Verse: "#8b5cf6", Person: "#f59e0b", "Family/Mentions": "#f59e0b" }).map(([label, color]) => (
                  <div key={label} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                    <span className="text-slate-300">{label}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {selectedNode && (
          <motion.div
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="w-80 bg-[#0d1321] border-r border-white/10 p-4 overflow-y-auto"
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2 py-1 bg-blue-100/10 text-blue-400 text-xs font-bold rounded">
                {(selectedNode.data as any)?.type}
              </span>
            </div>
            <h3 className="text-xl font-bold text-white mb-1" dir="rtl">
              {String((selectedNode.data as any)?.label || selectedNode.id)}
            </h3>
            <div className="mt-4 space-y-2">
              <button
                onClick={() => {
                  setCenterRef(String((selectedNode.data as any)?.ref || selectedNode.id));
                  setSelectedNode(null);
                }}
                className="w-full py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-lg text-sm border border-amber-500/20 transition-colors"
              >
                🔍 מרכז גרף כאן
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
