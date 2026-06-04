"use client";

import { useState, useCallback, useEffect } from "react";
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
  NodeProps,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Book,
  Scroll,
  Users,
  MapPin,
  Lightbulb,
  Scale,
  Clock,
  MessageCircle,
  Link2,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
} from "lucide-react";

// ── Type Definitions ──────────────────────────────────────

interface NodeData {
  label: string;
  hebrew?: string;
  type: string;
  ref?: string;
  text?: string;
  depth: number;
  expanded?: boolean;
}

// ── Custom Node Components ────────────────────────────────

function TorahNode({ data, selected }: NodeProps) {
  const d = data as any;
  const typeColors: Record<string, { bg: string; border: string; text: string }> = {
    Book: { bg: "bg-blue-50", border: "border-blue-500", text: "text-blue-700" },
    Chapter: { bg: "bg-indigo-50", border: "border-indigo-500", text: "text-indigo-700" },
    Verse: { bg: "bg-purple-50", border: "border-purple-500", text: "text-purple-700" },
    Person: { bg: "bg-green-50", border: "border-green-500", text: "text-green-700" },
    Place: { bg: "bg-amber-50", border: "border-amber-500", text: "text-amber-700" },
    Concept: { bg: "bg-pink-50", border: "border-pink-500", text: "text-pink-700" },
    Mitzvah: { bg: "bg-red-50", border: "border-red-500", text: "text-red-700" },
    Commentary: { bg: "bg-teal-50", border: "border-teal-500", text: "text-teal-700" },
    Event: { bg: "bg-cyan-50", border: "border-cyan-500", text: "text-cyan-700" },
    Law: { bg: "bg-orange-50", border: "border-orange-500", text: "text-orange-700" },
    TextUnit: { bg: "bg-slate-50", border: "border-slate-500", text: "text-slate-700" },
  };

  const colors = typeColors[d.type] || typeColors.TextUnit;
  const depthOpacity = Math.max(0.4, 1 - (d.depth || 0) * 0.08);
  const scale = Math.max(0.6, 1 - (d.depth || 0) * 0.05);

  return (
    <div
      className={`relative rounded-xl border-2 shadow-lg transition-all duration-300 ${colors.bg} ${colors.border} ${
        selected ? "ring-4 ring-blue-400 shadow-2xl scale-105" : "hover:shadow-xl hover:scale-105"
      }`}
      style={{
        opacity: depthOpacity,
        transform: `scale(${scale})`,
        minWidth: d.type === "Verse" ? "140px" : "100px",
        maxWidth: "200px",
      }}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 bg-slate-400" />
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-slate-400" />

      <div className="px-3 py-2">
        <div className="flex items-center gap-1.5 mb-1">
          <span className={`text-[10px] font-bold uppercase tracking-wider ${colors.text}`}>
            {d.type}
          </span>
          {d.expanded && <ChevronRight className="w-3 h-3 rotate-90 text-slate-400" />}
        </div>

        {d.hebrew && (
          <div className="text-base font-bold text-slate-900" dir="rtl">{d.hebrew}</div>
        )}
        <div className={`text-sm font-medium ${colors.text}`}>{d.label}</div>

        {d.ref && (
          <div className="text-[10px] text-slate-500 mt-1 font-mono">{d.ref}</div>
        )}

        {d.text && d.type === "Verse" && (
          <div className="mt-2 text-xs text-slate-700 leading-relaxed" dir="rtl">
            {d.text.substring(0, 60)}...
          </div>
        )}
      </div>
    </div>
  );
}

const nodeTypes = { torahNode: TorahNode };

// ── Multi-Level Data Generator ──────────────────────────

function buildDeepGraph(centerRef: string = "Genesis 1:1"): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  let nodeId = 0;

  function addNode(data: NodeData, x: number, y: number): string {
    const id = `n${nodeId++}`;
    nodes.push({
      id,
      type: "torahNode",
      position: { x, y },
      data: data as unknown as Record<string, unknown>,
    });
    return id;
  }

  function addEdge(from: string, to: string, label: string, animated: boolean = false) {
    edges.push({
      id: `e${from}-${to}`,
      source: from,
      target: to,
      label,
      animated,
      type: "smoothstep",
      style: { stroke: "#94a3b8", strokeWidth: 1.5 },
      labelStyle: { fontSize: "10px", fill: "#64748b" },
    });
  }

  // Level 0: Genesis (Book)
  const genesis = addNode(
    { label: "Genesis", hebrew: "בראשית", type: "Book", ref: "Genesis", depth: 0 },
    500,
    50
  );

  // Level 1: Chapters 1-3
  const chapters = [
    { label: "Chapter 1", hebrew: "פרק א", ref: "Genesis 1", verses: 31 },
    { label: "Chapter 2", hebrew: "פרק ב", ref: "Genesis 2", verses: 25 },
    { label: "Chapter 3", hebrew: "פרק ג", ref: "Genesis 3", verses: 24 },
  ];

  chapters.forEach((ch, i) => {
    const chNode = addNode(
      { label: ch.label, hebrew: ch.hebrew, type: "Chapter", ref: ch.ref, depth: 1 },
      200 + i * 300,
      180
    );
    addEdge(genesis, chNode, "PART_OF", i === 0);

    // Level 2: Verses (first 3 per chapter)
    for (let v = 1; v <= 3; v++) {
      const verseTexts: Record<string, string> = {
        "Genesis 1:1": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
        "Genesis 1:2": "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם",
        "Genesis 1:3": "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר",
        "Genesis 2:1": "וַיְכֻלּוּ הַשָּׁמַיִם וְהָאָרֶץ וְכָל־צְבָאָם",
        "Genesis 2:2": "וַיְכַל אֱלֹהִים בַּיּוֹם הַשְּׁבִיעִי מְלַאכְתּוֹ אֲשֶׁר עָשָׂה",
        "Genesis 3:1": "וְהַנָּחָשׁ הָיָה עָרוּם מִכֹּל חַיַּת הַשָּׂדֶה",
      };

      const ref = `${ch.ref}:${v}`;
      const vNode = addNode(
        {
          label: `${ch.hebrew}:${v}`,
          type: "Verse",
          ref,
          text: verseTexts[ref] || `Verse ${v}`,
          depth: 2,
        },
        150 + i * 300 + (v - 2) * 80,
        320 + (v % 2) * 60
      );
      addEdge(chNode, vNode, "PART_OF");

      // Level 3: Entities mentioned in verse
      if (ref === "Genesis 1:1") {
        const entities = [
          { label: "God", hebrew: "אֱלֹהִים", type: "Person" },
          { label: "Heaven", hebrew: "שָׁמַיִם", type: "Place" },
          { label: "Earth", hebrew: "אָרֶץ", type: "Place" },
        ];

        entities.forEach((ent, ei) => {
          const eNode = addNode(
            { label: ent.label, hebrew: ent.hebrew, type: ent.type, ref: ent.label, depth: 3 },
            100 + ei * 120,
            480
          );
          addEdge(vNode, eNode, "MENTIONS", true);

          // Level 4: Relationships of entities
          if (ent.label === "God") {
            const create = addNode(
              { label: "Creation", hebrew: "בְּרִיאָה", type: "Event", ref: "Creation", depth: 4 },
              200,
              620
            );
            addEdge(eNode, create, "PERFORMED", true);

            // Level 5: Related concepts
            const concepts = [
              { label: "Divine Will", hebrew: "רָצוֹן", type: "Concept" },
              { label: "Existence", hebrew: "מְצִיאוּת", type: "Concept" },
            ];
            concepts.forEach((c, ci) => {
              const cNode = addNode(
                { label: c.label, hebrew: c.hebrew, type: c.type, depth: 5 },
                150 + ci * 100,
                760
              );
              addEdge(create, cNode, "RELATED_TO");

              // Level 6: Sub-concepts
              const sub = addNode(
                { label: "Free Will", hebrew: "בְּחִירָה", type: "Concept", depth: 6 },
                250,
                900
              );
              addEdge(cNode, sub, "DERIVED_FROM");

              // Level 7: Legal implications
              const law = addNode(
                { label: "Moral Choice", hebrew: "בְּחִירָה מוּסָרִית", type: "Law", depth: 7 },
                250,
                1040
              );
              addEdge(sub, law, "REQUIRES");

              // Level 8: Practical applications
              const app = addNode(
                { label: "Repentance", hebrew: "תְּשׁוּבָה", type: "Mitzvah", depth: 8 },
                250,
                1180
              );
              addEdge(law, app, "ENABLES");

              // Level 9: Historical context
              const hist = addNode(
                { label: "Yom Kippur", hebrew: "יוֹם הַכִּפּוּרִים", type: "Event", depth: 9 },
                250,
                1320
              );
              addEdge(app, hist, "OBSERVED_ON");

              // Level 10: Modern commentary
              const comm = addNode(
                { label: "Rambam on Teshuvah", hebrew: "רמבם הלכות תשובה", type: "Commentary", depth: 10 },
                250,
                1460
              );
              addEdge(hist, comm, "COMMENTARY_ON");
            });
          }
        });
      }
    }
  });

  return { nodes, edges };
}

// ── Main Component ──────────────────────────────────────

export function AdvancedGraphExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [depthLevel, setDepthLevel] = useState(10);
  const [filterType, setFilterType] = useState<string | null>(null);

  useEffect(() => {
    const { nodes: initialNodes, edges: initialEdges } = buildDeepGraph();
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, []);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
      // Highlight path to this node
      const connectedEdges = edges.map((e) => ({
        ...e,
        animated: e.source === node.id || e.target === node.id,
        style: {
          ...e.style,
          stroke: e.source === node.id || e.target === node.id ? "#3b82f6" : "#94a3b8",
          strokeWidth: e.source === node.id || e.target === node.id ? 3 : 1,
        },
      }));
      setEdges(connectedEdges);
    },
    [edges, setEdges]
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        animated: false,
        style: { ...e.style, stroke: "#94a3b8", strokeWidth: 1 },
      }))
    );
  }, [setEdges]);

  const filteredNodes = filterType
    ? nodes.filter((n) => n.data?.type === filterType)
    : nodes;

  const filteredEdges = filterType
    ? edges.filter(
        (e) =>
          filteredNodes.some((n) => n.id === e.source) &&
          filteredNodes.some((n) => n.id === e.target)
      )
    : edges;

  const nodeTypesList = Array.from(new Set(nodes.map((n) => n.data?.type).filter(Boolean)));

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 p-3 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Depth:</span>
          <input
            type="range"
            min="1"
            max="10"
            value={depthLevel}
            onChange={(e) => setDepthLevel(Number(e.target.value))}
            className="w-24"
          />
          <span className="text-sm text-slate-600 dark:text-slate-400 w-6">{depthLevel}</span>
        </div>

        <div className="h-6 w-px bg-slate-300 dark:bg-slate-600" />

        <div className="flex items-center gap-1">
          <button
            onClick={() => setFilterType(null)}
            className={`px-2 py-1 text-xs rounded-md transition-colors ${
              !filterType ? "bg-blue-600 text-white" : "bg-slate-100 dark:bg-slate-700 text-slate-700"
            }`}
          >
            All
          </button>
          {nodeTypesList.map((t: any) => (
            <button
              key={t}
              onClick={() => setFilterType(filterType === t ? null : t)}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                filterType === t ? "bg-blue-600 text-white" : "bg-slate-100 dark:bg-slate-700 text-slate-700"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="flex-1" />

        <div className="text-sm text-slate-500">
          {filteredNodes.length} nodes | {filteredEdges.length} edges
        </div>
      </div>

      <div className="flex flex-1">
        {/* Graph */}
        <div className="flex-1">
          <ReactFlow
            nodes={filteredNodes}
            edges={filteredEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.1}
            maxZoom={2}
            connectionLineType={ConnectionLineType.SmoothStep}
          >
            <Background gap={16} size={1} />
            <Controls />
            <MiniMap
              nodeStrokeWidth={3}
              nodeColor={(n) => {
                const colors: Record<string, string> = {
                  Book: "#3b82f6",
                  Chapter: "#6366f1",
                  Verse: "#8b5cf6",
                  Person: "#22c55e",
                  Place: "#f59e0b",
                  Concept: "#ec4899",
                  Mitzvah: "#ef4444",
                  Commentary: "#14b8a6",
                  Event: "#06b6d4",
                  Law: "#f97316",
                  TextUnit: "#64748b",
                };
                return colors[n.data?.type as string] || "#999";
              }}
            />

            <Panel position="top-right" className="m-2">
              <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur p-3 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                  Graph Levels
                </h4>
                {[
                  { level: 0, label: "Book", desc: "ספר" },
                  { level: 1, label: "Chapter", desc: "פרק" },
                  { level: 2, label: "Verse", desc: "פסוק" },
                  { level: 3, label: "Entity", desc: "ישות" },
                  { level: 4, label: "Event", desc: "אירוע" },
                  { level: 5, label: "Concept", desc: "מושג" },
                  { level: 6, label: "Sub-concept", desc: "תת-מושג" },
                  { level: 7, label: "Law", desc: "הלכה" },
                  { level: 8, label: "Mitzvah", desc: "מצווה" },
                  { level: 9, label: "Event", desc: "מועד" },
                  { level: 10, label: "Commentary", desc: "פרשנות" },
                ].map((l) => (
                  <div key={l.level} className="flex items-center gap-2 text-xs">
                    <span className="w-5 text-right font-mono text-slate-400">{l.level}</span>
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <span className="text-slate-700 dark:text-slate-300">{l.label}</span>
                    <span className="text-slate-400 text-[10px]">{l.desc}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {/* Detail Panel */}
        {selectedNode && (
          <div className="w-80 bg-white dark:bg-slate-800 border-l border-slate-200 dark:border-slate-700 p-4 overflow-y-auto">
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-bold rounded">
                Level {((selectedNode.data as any)?.depth)}
              </span>
              <span className="text-xs text-slate-500">{((selectedNode.data as any)?.type)}</span>
            </div>

            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1" dir="rtl">
              {((selectedNode.data as any)?.hebrew) || ((selectedNode.data as any)?.label)}
            </h3>
            <p className="text-sm text-slate-500 mb-4">{((selectedNode.data as any)?.label)}</p>

            {((selectedNode.data as any)?.ref) ? (
              <div className="mb-3 p-2 bg-slate-50 dark:bg-slate-700 rounded font-mono text-xs">
                {((selectedNode.data as any)?.ref)}
              </div>
            ) : null}

            {((selectedNode.data as any)?.text) ? (
              <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-700 rounded text-sm" dir="rtl">
                {((selectedNode.data as any)?.text)}
              </div>
            ) : null}

            <div className="space-y-2">
              <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors">
                חפש קשרים צולבים
              </button>
              <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors">
                הצג פרשנויות
              </button>
              <button className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors">
                גלה ישויות קשורות
              </button>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
              <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Connected Nodes</h4>
              <div className="space-y-1">
                {edges
                  .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                  .map((e) => {
                    const otherId = e.source === selectedNode.id ? e.target : e.source;
                    const otherNode = nodes.find((n) => n.id === otherId);
                    return (
                      <div key={e.id} className="flex items-center gap-2 text-xs p-2 bg-slate-50 dark:bg-slate-700 rounded">
                        <Link2 className="w-3 h-3 text-slate-400" />
                        <span className="text-slate-600 dark:text-slate-300">{((otherNode?.data as any)?.label)}</span>
                        <span className="text-slate-400">({e.label})</span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
