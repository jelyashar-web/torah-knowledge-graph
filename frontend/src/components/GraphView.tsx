"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Panel,
  ConnectionLineType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Book, Scroll, Users, MapPin, Lightbulb, Scale } from "lucide-react";

const NODE_TYPES = {
  Book: { color: "#3b82f6", bg: "#dbeafe" },
  Chapter: { color: "#6366f1", bg: "#e0e7ff" },
  Verse: { color: "#8b5cf6", bg: "#ede9fe" },
  Person: { color: "#22c55e", bg: "#dcfce7" },
  Place: { color: "#f59e0b", bg: "#fef3c7" },
  Concept: { color: "#ec4899", bg: "#fce7f3" },
  Mitzvah: { color: "#ef4444", bg: "#fee2e2" },
  TextUnit: { color: "#14b8a6", bg: "#ccfbf1" },
};

export function GraphView() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    // Build animated demo graph: Genesis 1 with entities
    const demoNodes: Node[] = [
      {
        id: "genesis",
        type: "default",
        position: { x: 400, y: 50 },
        data: { label: "בראשית", type: "Book", ref: "Genesis", hebrew: "בראשית" },
        style: {
          background: NODE_TYPES.Book.bg,
          border: `2px solid ${NODE_TYPES.Book.color}`,
          borderRadius: "16px",
          padding: "12px 24px",
          fontWeight: "bold",
          fontSize: "16px",
          color: NODE_TYPES.Book.color,
          boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
          transition: "all 0.3s ease",
        },
      },
      {
        id: "gen-1",
        type: "default",
        position: { x: 400, y: 180 },
        data: { label: "פרק א", type: "Chapter", ref: "Genesis 1", number: 1 },
        style: {
          background: NODE_TYPES.Chapter.bg,
          border: `2px solid ${NODE_TYPES.Chapter.color}`,
          borderRadius: "12px",
          padding: "8px 16px",
          color: NODE_TYPES.Chapter.color,
          transition: "all 0.3s ease",
        },
      },
      {
        id: "gen-1-1",
        type: "default",
        position: { x: 150, y: 320 },
        data: { label: "א:א", type: "Verse", ref: "Genesis 1:1", text: "בְּרֵאשִׁית בָּרָא אֱלֹהִים..." },
        style: {
          background: NODE_TYPES.Verse.bg,
          border: `2px solid ${NODE_TYPES.Verse.color}`,
          borderRadius: "8px",
          padding: "6px 12px",
          fontSize: "13px",
          color: NODE_TYPES.Verse.color,
          transition: "all 0.3s ease",
        },
      },
      {
        id: "gen-1-2",
        type: "default",
        position: { x: 400, y: 320 },
        data: { label: "א:ב", type: "Verse", ref: "Genesis 1:2", text: "וְהָאָרֶץ הָיְתָה תֹהוּ..." },
        style: {
          background: NODE_TYPES.Verse.bg,
          border: `2px solid ${NODE_TYPES.Verse.color}`,
          borderRadius: "8px",
          padding: "6px 12px",
          fontSize: "13px",
          color: NODE_TYPES.Verse.color,
          transition: "all 0.3s ease",
        },
      },
      {
        id: "gen-1-3",
        type: "default",
        position: { x: 650, y: 320 },
        data: { label: "א:ג", type: "Verse", ref: "Genesis 1:3", text: "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר..." },
        style: {
          background: NODE_TYPES.Verse.bg,
          border: `2px solid ${NODE_TYPES.Verse.color}`,
          borderRadius: "8px",
          padding: "6px 12px",
          fontSize: "13px",
          color: NODE_TYPES.Verse.color,
          transition: "all 0.3s ease",
        },
      },
      {
        id: "elohim",
        type: "default",
        position: { x: 800, y: 50 },
        data: { label: "אלהים", type: "Concept", ref: "God", hebrew: "אֱלֹהִים" },
        style: {
          background: NODE_TYPES.Concept.bg,
          border: `2px solid ${NODE_TYPES.Concept.color}`,
          borderRadius: "16px",
          padding: "12px 24px",
          fontWeight: "bold",
          color: NODE_TYPES.Concept.color,
          boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
          transition: "all 0.3s ease",
        },
      },
      {
        id: "light",
        type: "default",
        position: { x: 800, y: 180 },
        data: { label: "אוֹר", type: "Concept", ref: "Light" },
        style: {
          background: NODE_TYPES.Concept.bg,
          border: `2px solid ${NODE_TYPES.Concept.color}`,
          borderRadius: "12px",
          padding: "8px 16px",
          color: NODE_TYPES.Concept.color,
          transition: "all 0.3s ease",
        },
      },
      {
        id: "heaven",
        type: "default",
        position: { x: 50, y: 50 },
        data: { label: "שָׁמַיִם", type: "Place", ref: "Heaven" },
        style: {
          background: NODE_TYPES.Place.bg,
          border: `2px solid ${NODE_TYPES.Place.color}`,
          borderRadius: "12px",
          padding: "8px 16px",
          color: NODE_TYPES.Place.color,
          transition: "all 0.3s ease",
        },
      },
      {
        id: "earth",
        type: "default",
        position: { x: 50, y: 180 },
        data: { label: "אָרֶץ", type: "Place", ref: "Earth" },
        style: {
          background: NODE_TYPES.Place.bg,
          border: `2px solid ${NODE_TYPES.Place.color}`,
          borderRadius: "12px",
          padding: "8px 16px",
          color: NODE_TYPES.Place.color,
          transition: "all 0.3s ease",
        },
      },
    ];

    const demoEdges: Edge[] = [
      { id: "e1", source: "genesis", target: "gen-1", label: "PART_OF", animated: true, type: "smoothstep" },
      { id: "e2", source: "gen-1", target: "gen-1-1", label: "PART_OF", type: "smoothstep" },
      { id: "e3", source: "gen-1", target: "gen-1-2", label: "PART_OF", type: "smoothstep" },
      { id: "e4", source: "gen-1", target: "gen-1-3", label: "PART_OF", type: "smoothstep" },
      { id: "e5", source: "gen-1-1", target: "elohim", label: "MENTIONS", animated: true, type: "smoothstep" },
      { id: "e6", source: "gen-1-1", target: "heaven", label: "MENTIONS", type: "smoothstep" },
      { id: "e7", source: "gen-1-1", target: "earth", label: "MENTIONS", type: "smoothstep" },
      { id: "e8", source: "gen-1-3", target: "light", label: "MENTIONS", animated: true, type: "smoothstep" },
      { id: "e9", source: "gen-1-1", target: "gen-1-2", label: "NEXT", type: "smoothstep" },
      { id: "e10", source: "gen-1-2", target: "gen-1-3", label: "NEXT", type: "smoothstep" },
      { id: "e11", source: "light", target: "elohim", label: "CREATED_BY", type: "smoothstep" },
    ];

    setNodes(demoNodes);
    setEdges(demoEdges);
    setStats({ nodes: demoNodes.length, edges: demoEdges.length });
  }, []);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    // Highlight connected edges
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        animated: e.source === node.id || e.target === node.id,
        style: {
          ...e.style,
          stroke: e.source === node.id || e.target === node.id ? "#3b82f6" : "#94a3b8",
          strokeWidth: e.source === node.id || e.target === node.id ? 3 : 1,
        },
      }))
    );
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        animated: false,
        style: { ...e.style, stroke: "#94a3b8", strokeWidth: 1 },
      }))
    );
  }, []);

  return (
    <div className="flex flex-col md:flex-row gap-4">
      <div className="flex-1 h-[600px] rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          fitView
          connectionLineType={ConnectionLineType.SmoothStep}
          attributionPosition="bottom-left"
        >
          <Background gap={12} size={1} />
          <Controls />
          <MiniMap
            nodeStrokeWidth={3}
            nodeColor={(n) => NODE_TYPES[n.data?.type as keyof typeof NODE_TYPES]?.color || "#999"}
          />
          <Panel position="top-right" className="bg-white/90 dark:bg-slate-900/90 p-3 rounded-lg shadow-lg backdrop-blur">
            <div className="text-xs space-y-1">
              <div className="font-semibold text-slate-900 dark:text-white">Nodes: {stats.nodes}</div>
              <div className="font-semibold text-slate-900 dark:text-white">Edges: {stats.edges}</div>
              <div className="mt-2 space-y-1">
                {Object.entries(NODE_TYPES).map(([type, { color }]) => (
                  <div key={type} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                    <span className="text-slate-600 dark:text-slate-300">{type}</span>
                  </div>
                ))}
              </div>
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {/* Node Detail Panel */}
      {selectedNode && (
        <div className="w-full md:w-72 bg-white dark:bg-slate-800 rounded-xl p-4 shadow-lg border border-slate-200 dark:border-slate-700">
          <h3 className="font-bold text-lg mb-2 text-slate-900 dark:text-white">
            {String(selectedNode.data?.hebrew || selectedNode.data?.label || "")}
          </h3>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-slate-500">Type: </span>
              <span className="font-medium">{String(selectedNode.data?.type || "")}</span>
            </div>
            {selectedNode.data?.ref ? (
              <div>
                <span className="text-slate-500">Reference: </span>
                <span className="font-medium">{String(selectedNode.data?.ref || "")}</span>
              </div>
            ) : null}
            {selectedNode.data?.text ? (
              <div className="mt-3 p-2 bg-slate-50 dark:bg-slate-700 rounded text-sm" dir="rtl">
                {String(selectedNode.data?.text || "")}
              </div>
            ) : null}
            <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700">
              <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm">
                חפש קשרים צולבים
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
