# Torah Knowledge Graph — UI Design Document

**Version:** 1.0.0
**Date:** 2026-06-04
**Status:** Production-Ready Design Specification

---

## Table of Contents

1. [Design System Overview](#1-design-system-overview)
2. [Global Layout & Navigation](#2-global-layout--navigation)
3. [View Specifications](#3-view-specifications)
   - 3.1 [Local Graph View](#31-local-graph-view)
   - 3.2 [Topic Graph View](#32-topic-graph-view)
   - 3.3 [Person Graph View](#33-person-graph-view)
   - 3.4 [Book Graph View](#34-book-graph-view)
   - 3.5 [Global Graph View](#35-global-graph-view)
4. [Shared Components](#4-shared-components)
   - 4.1 [Node Detail Panel](#41-node-detail-panel)
   - 4.2 [Search Interface](#42-search-interface)
   - 4.3 [Graph Layer Selector](#43-graph-layer-selector)
5. [Component Hierarchy](#5-component-hierarchy)
6. [State Management](#6-state-management)
7. [Design Tokens (Tailwind Theme)](#7-design-tokens-tailwind-theme)
8. [Responsive Design](#8-responsive-design)
9. [Accessibility](#9-accessibility)
10. [Performance Optimizations](#10-performance-optimizations)

---

## 1. Design System Overview

### Philosophy

The Torah Knowledge Graph platform embodies the principle that **sacred knowledge is interconnected**. The design balances reverence for the content with clarity of information architecture. Every visual decision serves the user's journey from curiosity to understanding.

**Core Principles:**

1. **Clarity Over Decoration** — The graph is the content; chrome is minimal
2. **Progressive Disclosure** — Surface summaries, reveal details on demand
3. **Context Preservation** — Users always know where they are in the knowledge space
4. **Respectful Aesthetics** — Warm, scholarly palette; no flashy or distracting animations
5. **Accessibility First** — The graph must be navigable by keyboard and screen reader

### Terminology

| Term | Definition |
|------|------------|
| **Node** | A discrete entity in the graph (Person, Book, Concept, Verse, Commentary) |
| **Edge** | A relationship between two nodes, with a typed label |
| **Hop** | A single edge traversal from one node to another |
| **Neighborhood** | All nodes reachable within N hops from a selected node |
| **Layer** | A mystical overlay (Promises, Segulot, Tikkun, Middot, Divine Names, Sefirot, Soul Root) that highlights relevant nodes and edges |
| **View** | A distinct visualization mode optimized for a specific exploration pattern |

---

## 2. Global Layout & Navigation

### App Shell

The application uses a **three-zone layout**:

```
┌─────────────────────────────────────────────────────────────┐
│  Top Bar (Omnibar + View Switcher + Layer Toggle)          │  56px
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│  Graph Canvas            │  Detail Sidebar (collapsible)    │
│  (primary focus area)    │  400px wide, 100% height        │
│                          │                                  │
│  ~70% viewport           │  ~30% viewport                   │
│                          │                                  │
├──────────────────────────┴──────────────────────────────────┤
│  Status Bar (node count, performance metrics)               │  24px
└─────────────────────────────────────────────────────────────┘
```

**Behavior:**
- The Detail Sidebar collapses to a floating action button (FAB) on mobile, expanding to full-screen overlay when activated
- The Graph Canvas occupies all remaining space after the Top Bar and Sidebar
- A subtle 1px border (`border-slate-200`) separates the Sidebar from the Canvas

### Navigation Patterns

**Primary Navigation — View Switcher:**

A segmented control in the Top Bar allows switching between views:

```
[ Local ] [ Topic ] [ Person ] [ Book ] [ Global ]
```

- Active segment: `bg-amber-700 text-white`
- Inactive segment: `bg-transparent text-slate-600 hover:text-slate-900`
- Transition: 150ms ease-out background-color change
- Keyboard: Arrow keys navigate segments, Enter activates

**Secondary Navigation — Breadcrumb:**

Below the Top Bar, a breadcrumb trail shows the current exploration path:

```
Global > Shabbat > Commentaries > Rashi > Commentary on Genesis 2:2
```

- Each segment is clickable to jump back to that context
- Current segment: `font-medium text-slate-900`
- Ancestor segments: `text-slate-500 hover:text-amber-700 underline`
- Separator: `text-slate-300` chevron icon

**Tertiary Navigation — Mini-Map:**

Available only in Global Graph View. A thumbnail representation of the full graph sits in the bottom-left corner of the Canvas (160x120px), with a viewport rectangle showing the current visible region.

---

## 3. View Specifications

### 3.1 Local Graph View

**Purpose:** Explore the immediate neighborhood of any node, up to 3 hops away.

**Entry Point:** Click any node in any view; the view switches to Local Graph centered on that node.

**Interaction Flow:**

1. **Initial State:** Selected node centered, 1-hop neighborhood rendered
2. **Depth Expansion:** User adjusts depth slider (1-3); new nodes animate in from edges
3. **Node Exploration:** Click any visible node to re-center the graph on that node
4. **Pinning:** Right-click (or long-press on touch) a node to pin it in place; pinned nodes ignore force-directed forces
5. **Return:** Breadcrumb or "Back to Previous View" button

**Depth Slider Control:**

```
Depth: [1] — [2] — [3]
       ○     ●     ○
```

- Positioned as a floating card in the top-left of the Canvas
- Card styling: `bg-white/90 backdrop-blur shadow-md rounded-lg p-3`
- Slider uses `input[type="range"]` with custom thumb styling
- Thumb: `w-4 h-4 bg-amber-700 rounded-full`
- Track: `h-1 bg-slate-200`
- Labels below each step: `text-xs text-slate-500`
- Active step label: `font-semibold text-amber-700`
- Changing depth triggers a 300ms force-layout re-simulation with enter/exit animations

**Node Size Scaling:**

Node radius is proportional to the logarithm of its connection count within the current neighborhood:

```
radius = baseRadius + log2(connectionCount + 1) * scaleFactor
```

- `baseRadius`: 24px (desktop), 16px (mobile)
- `scaleFactor`: 4px
- Maximum radius capped at 48px to prevent overwhelming visual dominance
- Selected node: +4px halo using `ring-2 ring-amber-400`

**Edge Thickness Scaling:**

Edge stroke width is proportional to relationship strength (0.0-1.0):

```
strokeWidth = 1px + strength * 3px
```

- Minimum: 1px (`stroke-slate-300`)
- Maximum: 4px (`stroke-slate-400`)
- Selected path (from center node to hovered node): `stroke-amber-500` with `stroke-width: 3px`

**Color Coding by Node Type:**

| Node Type | Fill Color | Stroke Color | Text Label Color |
|-----------|-----------|--------------|-----------------|
| Person | `bg-blue-50` | `stroke-blue-300` | `text-blue-900` |
| Book | `bg-amber-50` | `stroke-amber-300` | `text-amber-900` |
| Concept | `bg-emerald-50` | `stroke-emerald-300` | `text-emerald-900` |
| Verse | `bg-violet-50` | `stroke-violet-300` | `text-violet-900` |
| Commentary | `bg-rose-50` | `stroke-rose-300` | `text-rose-900` |

All nodes use a 2px stroke, `rounded-lg` shape (8px radius), and a subtle `shadow-sm`.

**Force-Directed Layout with Pinning:**

The layout uses a force-directed simulation with the following parameters:

- **Link force:** `distance = 100px`, `strength = 0.5`
- **Charge force:** `-300` repulsion between nodes
- **Center force:** Pulls toward viewport center with `strength = 0.05`
- **Collision force:** `radius = nodeRadius + 4px padding`
- **Alpha decay:** `0.02` per tick for smooth settling

**Pinning Behavior:**
- Right-click node → context menu with "Pin Node" option
- Pinned nodes: `stroke-dashed stroke-slate-500`
- Pinned nodes have fixed `fx, fy` coordinates in the simulation
- "Unpin All" button in the floating controls card

**Animation:**
- New nodes entering: fade in + scale from 0.8 to 1.0 over 200ms
- Nodes exiting: fade out over 150ms
- Layout transitions: 300ms ease-out using D3 transition

---

### 3.2 Topic Graph View

**Purpose:** Explore all nodes related to a selected topic, clustered by type.

**Entry Point:** Search for a topic or select from a "Popular Topics" grid on the home screen.

**Interaction Flow:**

1. **Topic Selection:** User selects a topic (e.g., "Charity", "Shabbat")
2. **Initial Render:** All related nodes appear, clustered by node type in a circular or hive layout
3. **Filtering:** User toggles relationship types to filter edges
4. **Timeline Toggle:** User switches to timeline view to see historical development
5. **Drill-down:** Click any node to open Local Graph View for that node

**Topic Selection Interface:**

A search-driven dropdown with category suggestions:

```
┌────────────────────────────────────────┐
│  Search topics...                      │
├────────────────────────────────────────┤
│  Popular Topics                        │
│  [Charity] [Shabbat] [Prayer]         │
│  [Redemption] [Torah Study] [Love]    │
├────────────────────────────────────────┤
│  Recent Topics                         │
│  Charity, Shabbat, Prayer...         │
└────────────────────────────────────────┘
```

- Dropdown: `bg-white shadow-lg rounded-lg border border-slate-200`
- Topic chip: `bg-slate-100 hover:bg-amber-50 text-slate-700 hover:text-amber-800 rounded-full px-3 py-1 text-sm transition-colors`

**Node Clustering by Type:**

When a topic is selected, nodes are arranged in **concentric rings** by type:

- **Inner ring (radius 0-150px):** Concepts directly defining the topic
- **Middle ring (radius 150-300px):** Verses and Books discussing the topic
- **Outer ring (radius 300-450px):** People and Commentaries related to the topic

Each ring is labeled with a subtle `text-slate-400 text-xs uppercase tracking-wide` label positioned at the ring's top.

**Relationship Type Filter:**

A filter bar below the Top Bar:

```
Show relationships: [✓ teaches] [✓ comments on] [✓ mentions] [✓ is promised by]
```

- Each filter is a toggle chip: `border border-slate-300 rounded-md px-2 py-1 text-xs`
- Active: `bg-amber-100 border-amber-300 text-amber-800`
- Inactive: `bg-white text-slate-500`
- Edge count badge on each chip: `bg-slate-200 text-slate-600 rounded-full px-1.5 py-0.5 text-[10px]`

**Timeline View:**

Toggle switch next to the relationship filter: `[Graph] [Timeline]`

In Timeline view:
- X-axis: Time (BCE to present, logarithmic scale for ancient periods)
- Y-axis: Node type (stacked lanes: People, Books, Commentaries)
- Nodes positioned by their historical date
- Edges shown as curved lines connecting related nodes across time
- Zoom to era: Click and drag to select a time range; view zooms to that range
- "Reset Zoom" button appears when zoomed

---

### 3.3 Person Graph View

**Purpose:** Explore biographical connections of Torah scholars and figures.

**Entry Point:** Search for a person or select from a "Notable Figures" carousel.

**Interaction Flow:**

1. **Person Selection:** User selects a person (e.g., "Rashi", "Arizal")
2. **Initial Render:** Person node centered with connections radiating outward by type
3. **Connection Exploration:** Click any connected node to see its relationship to the center person
4. **Timeline Toggle:** View life events chronologically
5. **Map Toggle:** View geographic distribution of connections

**Connection Type Visualization:**

Edges are styled by relationship type:

| Relationship | Edge Style | Color |
|-------------|-----------|-------|
| Teacher | Solid, `stroke-width: 3px` | `stroke-blue-500` |
| Student | Dashed, `stroke-width: 2px` | `stroke-blue-400` |
| Commentator | Dotted, `stroke-width: 2px` | `stroke-rose-400` |
| Family | Solid, `stroke-width: 2px` | `stroke-emerald-400` |
| Contemporary | Solid, `stroke-width: 1px` | `stroke-slate-300` |

Edge labels appear on hover: `bg-white/90 text-slate-700 text-xs px-2 py-1 rounded shadow-sm`

**Timeline of Life Events:**

Toggle: `[Network] [Timeline]`

Timeline shows:
- Horizontal axis: Years of the person's life
- Vertical lanes: Event categories (Birth, Death, Major Works, Travels, Teachers Met)
- Events as markers on lanes
- Click event → open detail panel with full description
- Connected people's life spans shown as background bars for context

**Geographic Map Overlay:**

Toggle: `[Network] [Map]`

Map integration:
- Uses a simplified historical map (not modern political boundaries)
- Nodes positioned at known geographic coordinates
- Clustering for nodes in same city/region (e.g., "Medieval Provence")
- Zoom levels: World → Region → City
- Heat map layer showing concentration of Torah activity by region
- Connection lines curve along plausible travel routes

---

### 3.4 Book Graph View

**Purpose:** Explore structural and content relationships of Torah texts.

**Entry Point:** Search for a book or select from a "Canon Browser" tree.

**Interaction Flow:**

1. **Book Selection:** User selects a book (e.g., "Genesis", "Zohar")
2. **Initial Render:** Hierarchical tree of chapters/verses
3. **Commentary Toggle:** Show/hide commentaries mapped to specific verses
4. **Cross-Reference Toggle:** Show lines connecting related verses across books
5. **Drill-down:** Click a verse to see all commentaries and connections

**Chapter/Verse Hierarchy Tree:**

A hybrid tree + graph visualization:

- **Left side (40%):** Collapsible tree of books → chapters → verses
  - Tree node: `flex items-center gap-2 py-1 px-2 hover:bg-slate-50 rounded`
  - Expand/collapse: Chevron icon `w-4 h-4 text-slate-400`
  - Selected node: `bg-amber-50 border-l-2 border-amber-500`
- **Right side (60%):** Graph of the selected chapter/verse and its connections
  - Graph updates as tree selection changes
  - Smooth transition: 300ms pan/zoom to center the newly selected node

**Commentary Mapping:**

When a verse is selected, commentaries appear as satellite nodes:

```
        [Rashi]
           |
    [Verse Node] — [Ibn Ezra]
           |
        [Ramban]
```

- Commentary nodes: `rounded-full` (circle shape) instead of `rounded-lg`
- Size proportional to commentary length (word count)
- Color: `bg-rose-50 stroke-rose-300` (Commentary node type)
- Hover commentary node: preview first 100 characters in tooltip
- Click commentary node: open full text in detail panel

**Cross-References Visualization:**

Cross-references between verses shown as **arced lines** connecting nodes:
- Reference type labeled on hover (e.g., "Parallel passage", "Allusion", "Source")
- Arc height proportional to "distance" between books (higher arc = more different books)
- Multiple references between same verses: parallel arcs with slight offset
- Filter by reference type in a dropdown

---

### 3.5 Global Graph View

**Purpose:** Navigate the entire knowledge graph with zoom-level aggregation.

**Entry Point:** Default view on app load, or select "Global" from View Switcher.

**Interaction Flow:**

1. **Initial Render:** Aggregated view showing major clusters (Torah, Nevi'im, Ketuvim, Talmud, Kabbalah, etc.)
2. **Zoom In:** Reveals sub-clusters, then individual nodes
3. **Search/Filter:** Narrow the visible graph to relevant subset
4. **Pan/Drag:** Explore different regions
5. **Select Node:** Transition to Local Graph View

**Zoom-Level Aggregation:**

| Zoom Level | Visible Elements | Aggregation |
|-----------|-----------------|-------------|
| 0-20% | Major corpora (Tanakh, Talmud, Midrash, Kabbalah) | Nodes = corpora, edges = cross-references |
| 20-40% | Books within corpora | Nodes = books, edges = commentary relationships |
| 40-60% | Chapters/Sections | Nodes = chapters, edges = structural connections |
| 60-80% | Individual verses/concepts | Nodes = verses/concepts, edges = citations |
| 80-100% | Full detail with commentaries | All node types visible |

**Performance Limits:**

- Maximum rendered nodes: **500** (with virtualization for off-screen nodes)
- When graph exceeds 500 visible nodes: show aggregation warning badge
- Progressive loading: load 100 nodes initially, then stream additional nodes in batches of 50
- Loading indicator: `Skeleton` pulse animation on placeholder nodes

**Search and Filter Integration:**

The search bar in the Top Bar filters the global graph in real-time:
- Typing filters visible nodes to matches
- Empty search shows full graph (subject to zoom aggregation)
- Filter chips show active filters: `bg-amber-100 text-amber-800 rounded-full px-2 py-0.5 text-xs`

**Mini-Map Navigation:**

- Position: Bottom-left of Canvas, 160x120px
- Background: `bg-slate-100 rounded border border-slate-200`
- Viewport rectangle: `border-2 border-amber-500 bg-amber-500/10`
- Dragging the rectangle pans the main view
- Clicking on the mini-map centers the main view on that region
- Collapsible: Chevron button to collapse to 40x40px icon

---

## 4. Shared Components

### 4.1 Node Detail Panel

**Layout Decision:**
- **Desktop (>1024px):** Collapsible sidebar on the right, 400px wide
- **Tablet (768-1024px):** Collapsible sidebar on the right, 320px wide
- **Mobile (<768px):** Full-screen modal overlay, slide up from bottom

**Sidebar Behavior:**
- Collapse button: Chevron at the sidebar edge
- Collapsed state: Shows only node type icon and name vertically rotated
- Animation: 250ms ease-in-out width transition
- Resizable: Drag edge to resize between 320px and 480px

**Modal Behavior (Mobile):**
- Slide up from bottom with `transform translate-y` animation
- Backdrop: `bg-slate-900/50 backdrop-blur-sm`
- Drag handle at top: `w-12 h-1 bg-slate-300 rounded-full mx-auto mb-4`
- Swipe down to dismiss
- Full-screen button to expand to full viewport

**Tab Structure:**

```
┌─────────────────────────────────────────┐
│ [Node Name]                    [×]      │
│ [Node Type Badge]                       │
├─────────────────────────────────────────┤
│ [Sources] [Connections] [Citations] [Related] │
├─────────────────────────────────────────┤
│                                         │
│  Tab Content                            │
│                                         │
└─────────────────────────────────────────┘
```

**Tab Styling:**
- Active tab: `border-b-2 border-amber-600 text-amber-700 font-medium`
- Inactive tab: `text-slate-500 hover:text-slate-700`
- Tab bar: `border-b border-slate-200`

**Sources Tab:**

Displays exact citations with a copy button:

```
┌─────────────────────────────────────────┐
│ Source Texts                            │
│                                         │
│ 📖 Babylonian Talmud, Tractate Shabbat  │
│    127a                                 │
│    [Copy] [View in Context]             │
│                                         │
│ 📖 Zohar, Parashat Vayakhel             │
│    198b                                 │
│    [Copy] [View in Context]             │
└─────────────────────────────────────────┘
```

- Source item: `border border-slate-200 rounded-lg p-3 hover:border-amber-300 transition-colors`
- Copy button: `text-slate-400 hover:text-amber-600` icon button
- "View in Context" button: `text-amber-700 text-sm hover:underline`

**Connections Tab:**

Split into Inbound and Outbound sections:

```
Inbound (12)
├─ taught by → [Moses Maimonides]
├─ commented on by → [Rashi]
└─ mentioned in → [Zohar, Vayakhel]

Outbound (8)
├─ teaches → [Charity]
├─ is source for → [Shulchan Aruch]
└─ is mentioned by → [Ramban on Genesis]
```

- Section header: `font-semibold text-slate-800 text-sm uppercase tracking-wide mt-4 mb-2`
- Connection item: `flex items-center gap-2 py-1.5 hover:bg-slate-50 rounded px-2 cursor-pointer`
- Relationship label: `text-slate-500 text-xs`
- Target node: `text-slate-900 font-medium text-sm`
- Click target node: navigate to that node's Local Graph

**Citations Tab:**

Shows text snippets with surrounding context:

```
┌─────────────────────────────────────────┐
│ From: Zohar, Vayakhel 198b              │
│                                         │
│ ...and regarding the matter of charity, │
│ it is written that one who gives        │
│ generously...                           │
│                                         │
│ [Show Full Passage]                     │
└─────────────────────────────────────────┘
```

- Citation card: `bg-slate-50 border border-slate-200 rounded-lg p-4`
- Source header: `text-xs text-slate-500 font-medium mb-2`
- Quoted text: `text-slate-800 text-sm leading-relaxed italic`
- "Show Full Passage" button: `text-amber-700 text-sm mt-3 hover:underline`
- Hebrew text (if present): `font-hebrew text-right dir-rtl` (if mixed, use `dir="auto"`)

**Related Topics Tab:**

Grid of similar nodes with similarity score:

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Tzedakah    │ │ Gemilut     │ │ Ma'aser     │
│ 92% match   │ │ Hasadim     │ │ 78% match   │
│ [Concept]   │ │ 85% match   │ │ [Concept]   │
└─────────────┘ └─────────────┘ └─────────────┘
```

- Related node card: `bg-white border border-slate-200 rounded-lg p-3 hover:shadow-md hover:border-amber-300 transition-all cursor-pointer`
- Similarity badge: `bg-amber-100 text-amber-800 text-[10px] font-semibold rounded-full px-2 py-0.5`
- Node type badge: `text-slate-500 text-[10px] uppercase mt-1`

---

### 4.2 Search Interface

**Omnibar:**

Positioned in the Top Bar, center-aligned:

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo]    🔍 Search nodes, topics, people, books...    [?] │
└─────────────────────────────────────────────────────────────┘
```

- Input: `bg-slate-100 border-transparent focus:bg-white focus:border-amber-500 rounded-full px-4 py-2 w-96`
- Placeholder: `text-slate-400`
- Focus ring: `ring-2 ring-amber-500/20`
- Clear button (when text present): `text-slate-400 hover:text-slate-600`

**Autocomplete with Fuzzy Matching:**

```
┌────────────────────────────────────────┐
│  Search: "shab"                        │
├────────────────────────────────────────┤
│  Suggestions                           │
│  🔍 Shabbat (Concept)                   │
│  🔍 Shabbat 23a (Verse)                 │
│  🔍 Shabbat candles (Concept)           │
├────────────────────────────────────────┤
│  Recent Searches                       │
│  Charity, Rashi, Genesis...            │
└────────────────────────────────────────┘
```

- Dropdown: `bg-white shadow-xl rounded-lg border border-slate-200 mt-1`
- Fuzzy match highlighting: Matched characters `font-bold text-amber-700`
- Category grouping: `text-xs text-slate-400 uppercase tracking-wide px-3 py-2`
- Suggestion item: `px-3 py-2 hover:bg-slate-50 cursor-pointer flex items-center gap-2`
- Keyboard navigation: Arrow up/down to navigate, Enter to select, Escape to close
- Maximum 8 suggestions shown

**Faceted Filters:**

Filter panel slides out from the left when the filter button is clicked:

```
┌────────────────────────────────────────┐
│ Filters                                │
│ [Clear All]                            │
├────────────────────────────────────────┤
│ Node Type                              │
│ [✓] Person (45)                       │
│ [✓] Book (23)                          │
│ [ ] Concept (189)                      │
│ [✓] Verse (412)                        │
│ [ ] Commentary (67)                    │
├────────────────────────────────────────┤
│ Source Text                            │
│ [✓] Tanakh                            │
│ [ ] Talmud                             │
│ [ ] Zohar                              │
│ [ ] Midrash                            │
├────────────────────────────────────────┤
│ Date / Period                          │
│ [Any time]                             │
│ [Before Common Era]                     │
│ [0-500 CE]                             │
│ [500-1000 CE]                          │
│ [1000-1500 CE]                         │
│ [1500-present]                         │
└────────────────────────────────────────┘
```

- Filter panel: `bg-white shadow-lg w-72 h-full border-r border-slate-200`
- Section header: `font-semibold text-slate-800 text-sm mt-4 mb-2`
- Checkbox: Custom styled `w-4 h-4 rounded border-slate-300 text-amber-600 focus:ring-amber-500`
- Count badge: `text-slate-400 text-xs ml-auto`
- "Clear All" button: `text-amber-700 text-sm hover:underline`

**Full-Text + Vector Hybrid Search:**

- Full-text search: Matches node names, descriptions, and citation text
- Vector search: Semantic similarity for conceptual matches
- Hybrid ranking: `score = 0.6 * text_score + 0.4 * vector_score`
- "Semantic matches" section in results shows vector-only matches

**Search Results Views:**

Toggle between list and mini-graph:

```
[ List ] [ Mini-Graph ]
```

**List View:**
- Vertical list of result cards
- Each card: Node name, type badge, 2-line description, relevance score bar
- Relevance bar: `h-1 bg-slate-200 rounded-full` with fill `bg-amber-500`
- Pagination: 20 results per page, infinite scroll optional

**Mini-Graph View:**
- Small force-directed graph (400x300px) showing result nodes and their immediate connections
- Same color coding as main graph
- Click node: open Local Graph View
- Hover node: tooltip with name and type

---

### 4.3 Graph Layer Selector

**Purpose:** Toggle mystical/semantic overlays that highlight nodes and edges belonging to specific Torah concepts.

**UI Position:** Floating toolbar in the top-right of the Canvas.

```
┌─────────────────────────────────────────┐
│  Layers                    [▼]          │
├─────────────────────────────────────────┤
│  [✓] Promises        🔵                │
│  [✓] Segulot         🟢                │
│  [ ] Tikkun          🟡                │
│  [✓] Middot          🟠                │
│  [ ] Divine Names    🔴                │
│  [ ] Sefirot         🟣                │
│  [ ] Soul Root       ⚪                │
│                                         │
│  [Highlight Mode: Replace]             │
│  [Show All Layers]                      │
└─────────────────────────────────────────┘
```

**Layer Toggle:**
- Checkbox + color dot + layer name
- Active layer: Checkbox checked, name `font-medium`
- Inactive layer: Checkbox unchecked, name `text-slate-400`

**Highlight Modes:**
- **Replace:** Only nodes/edges belonging to active layers are visible (default)
- **Overlay:** All nodes visible, active layer nodes get an additional glow/halo
- **Dim:** All nodes visible, inactive layer nodes are dimmed to 30% opacity

Mode selector: Dropdown `bg-white border border-slate-300 rounded px-2 py-1 text-sm`

**Layer-Specific Color Schemes:**

When a layer is active, nodes belonging to that layer receive an additional accent:

| Layer | Accent Color | Glow Effect |
|-------|-------------|-------------|
| Promises | `text-blue-500` | `shadow-[0_0_8px_rgba(59,130,246,0.4)]` |
| Segulot | `text-emerald-500` | `shadow-[0_0_8px_rgba(16,185,129,0.4)]` |
| Tikkun | `text-amber-500` | `shadow-[0_0_8px_rgba(245,158,11,0.4)]` |
| Middot | `text-orange-500` | `shadow-[0_0_8px_rgba(249,115,22,0.4)]` |
| Divine Names | `text-red-500` | `shadow-[0_0_8px_rgba(239,68,68,0.4)]` |
| Sefirot | `text-violet-500` | `shadow-[0_0_8px_rgba(139,92,246,0.4)]` |
| Soul Root | `text-slate-500` | `shadow-[0_0_8px_rgba(100,116,139,0.4)]` |

**Multiple Active Layers:**
- A node can belong to multiple layers
- If multiple layers are active, the node shows all relevant accent colors as a multi-color ring
- Ring segments: `conic-gradient` or stacked `border-color` segments

---

## 5. Component Hierarchy

### Top-Level Architecture

```
App
├── GraphProvider (Zustand + Context)
│   ├── TopBar
│   │   ├── Logo
│   │   ├── SearchInterface
│   │   │   ├── SearchInput
│   │   │   ├── AutocompleteDropdown
│   │   │   └── FilterPanel
│   │   ├── ViewSwitcher
│   │   └── LayerToggleButton
│   ├── BreadcrumbNav
│   ├── GraphCanvas
│   │   ├── GraphRenderer (SVG/Canvas/WebGL)
│   │   │   ├── NodeLayer
│   │   │   │   └── GraphNode (memoized)
│   │   │   ├── EdgeLayer
│   │   │   │   └── GraphEdge (memoized)
│   │   │   └── LabelLayer
│   │   │       └── NodeLabel
│   │   ├── FloatingControls
│   │   │   ├── DepthSlider (Local Graph only)
│   │   │   ├── ZoomControls
│   │   │   ├── LayoutControls
│   │   │   └── PinControls
│   │   └── MiniMap (Global Graph only)
│   ├── NodeDetailPanel
│   │   ├── PanelHeader
│   │   ├── TabBar
│   │   ├── SourcesTab
│   │   ├── ConnectionsTab
│   │   ├── CitationsTab
│   │   └── RelatedTopicsTab
│   ├── LayerSelectorPanel
│   │   ├── LayerToggleList
│   │   └── HighlightModeSelector
│   └── StatusBar
└── ToastContainer
```

### Component Props Interfaces

**GraphContainer (GraphCanvas):**

```typescript
interface GraphCanvasProps {
  view: 'local' | 'topic' | 'person' | 'book' | 'global';
  centerNodeId?: string;
  depth?: number; // 1-3, for local view
  selectedTopic?: string; // for topic view
  selectedPerson?: string; // for person view
  selectedBook?: string; // for book view
  filters: {
    nodeTypes: NodeType[];
    relationshipTypes: RelationshipType[];
    dateRange?: [number, number];
    sources?: SourceText[];
  };
  activeLayers: LayerType[];
  highlightMode: 'replace' | 'overlay' | 'dim';
  onNodeSelect: (nodeId: string) => void;
  onNodeHover: (nodeId: string | null) => void;
  onDepthChange?: (depth: number) => void;
}
```

**GraphNode:**

```typescript
interface GraphNodeProps {
  id: string;
  type: NodeType;
  label: string;
  x: number;
  y: number;
  radius: number;
  isSelected: boolean;
  isHovered: boolean;
  isPinned: boolean;
  layerAccents: LayerType[];
  connectionCount: number;
  onClick: (id: string) => void;
  onRightClick: (id: string, event: MouseEvent) => void;
  onMouseEnter: (id: string) => void;
  onMouseLeave: () => void;
}
```

**GraphEdge:**

```typescript
interface GraphEdgeProps {
  id: string;
  source: { x: number; y: number };
  target: { x: number; y: number };
  type: RelationshipType;
  strength: number; // 0.0 - 1.0
  isHighlighted: boolean;
  label?: string;
}
```

**ControlPanel (FloatingControls):**

```typescript
interface FloatingControlsProps {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  controls: ControlItem[];
  visible: boolean;
}

interface ControlItem {
  id: string;
  type: 'slider' | 'button' | 'toggle' | 'button-group';
  label: string;
  value?: number | boolean | string;
  options?: { label: string; value: string }[];
  onChange: (value: unknown) => void;
}
```

**NodeDetailPanel:**

```typescript
interface NodeDetailPanelProps {
  nodeId: string | null;
  layout: 'sidebar' | 'modal';
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: 'sources' | 'connections' | 'citations' | 'related';
}
```

### Composition Patterns

1. **Render Props for Graph Renderer:** The `GraphRenderer` accepts render props for custom node/edge components, allowing view-specific overrides without duplicating layout logic.

2. **Compound Components for Tabs:** `NodeDetailPanel` uses compound components (`NodeDetailPanel.Tab`, `NodeDetailPanel.Content`) to allow flexible tab configuration per node type.

3. **HOC for Memorization:** `withGraphMemo` HOC wraps node/edge components with custom `React.memo` comparison that only re-renders when position, selection state, or visual properties change.

---

## 6. State Management

### Architecture: React Context + Zustand

**Principle:** Separate "slow-moving" UI state from "fast-moving" graph data.

#### Zustand Store (Graph Data)

Responsible for frequently updated, complex graph state:

```typescript
interface GraphStore {
  // Nodes and edges
  nodes: GraphNode[];
  edges: GraphEdge[];
  
  // Viewport
  transform: { x: number; y: number; k: number };
  
  // Selection
  selectedNodeId: string | null;
  hoveredNodeId: string | null;
  
  // View configuration
  currentView: ViewType;
  viewConfig: ViewConfig;
  
  // Loading
  isLoading: boolean;
  loadingProgress: number;
  
  // Actions
  setNodes: (nodes: GraphNode[]) => void;
  setEdges: (edges: GraphEdge[]) => void;
  selectNode: (id: string | null) => void;
  hoverNode: (id: string | null) => void;
  setTransform: (transform: Transform) => void;
  setView: (view: ViewType, config?: ViewConfig) => void;
  expandNeighborhood: (nodeId: string, depth: number) => Promise<void>;
}
```

**Store Slices:**
- `useNodeStore`: Node data and selection
- `useEdgeStore`: Edge data and filtering
- `useViewportStore`: Pan, zoom, transform
- `useViewStore`: Current view and configuration

#### React Context (UI State)

Responsible for slowly changing, broadly consumed UI state:

```typescript
interface UIState {
  // Sidebar / Panel
  isDetailPanelOpen: boolean;
  detailPanelLayout: 'sidebar' | 'modal';
  
  // Filters
  activeFilters: FilterState;
  
  // Layers
  activeLayers: LayerType[];
  highlightMode: HighlightMode;
  
  // Search
  searchQuery: string;
  searchResults: SearchResult[];
  isSearchActive: boolean;
  
  // Global UI
  theme: 'light' | 'dark';
  notifications: Notification[];
}
```

**Context Providers:**
- `UIStateProvider`: Top-level, wraps entire app
- `FilterProvider`: For search filter state
- `LayerProvider`: For layer toggle state
- `SearchProvider`: For search query and results

### State Flow

```
User Action
    ↓
UI Context (React Context)
    ↓
Derived/computed values
    ↓
Zustand Action (if graph data changes)
    ↓
Graph update → Re-render GraphCanvas
    ↓
Memoized Node/Edge components (selective re-render)
```

**Example Flow — Node Selection:**
1. User clicks node → `GraphNode.onClick`
2. `selectNode(id)` called on Zustand store
3. Store updates `selectedNodeId`
4. `GraphCanvas` re-renders (but only nodes check `isSelected`)
5. `NodeDetailPanel` (subscribed to `selectedNodeId`) opens
6. Panel fetches node details via API (cached in Zustand)

### Graph Data Caching Strategy

- **LRU Cache:** Keep last 20 neighborhoods in memory
- **Cache Key:** `view:centerNodeId:depth:filtersHash`
- **Eviction:** When cache exceeds 50MB or 50 entries
- **Prefetching:** On hover, prefetch 1-hop neighborhood (low priority)

---

## 7. Design Tokens (Tailwind Theme)

### Color Palette

#### Node Type Colors

```javascript
// tailwind.config.ts
colors: {
  node: {
    person: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    book: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    concept: {
      50: '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10b981',
      600: '#059669',
      700: '#047857',
      800: '#065f46',
      900: '#064e3b',
    },
    verse: {
      50: '#f5f3ff',
      100: '#ede9fe',
      200: '#ddd6fe',
      300: '#c4b5fd',
      400: '#a78bfa',
      500: '#8b5cf6',
      600: '#7c3aed',
      700: '#6d28d9',
      800: '#5b21b6',
      900: '#4c1d95',
    },
    commentary: {
      50: '#fff1f2',
      100: '#ffe4e6',
      200: '#fecdd3',
      300: '#fda4af',
      400: '#fb7185',
      500: '#f43f5e',
      600: '#e11d48',
      700: '#be123c',
      800: '#9f1239',
      900: '#881337',
    },
  },
}
```

#### Layer Accent Colors

```javascript
colors: {
  layer: {
    promises: '#3b82f6',
    segulot: '#10b981',
    tikkun: '#f59e0b',
    middot: '#f97316',
    'divine-names': '#ef4444',
    sefirot: '#8b5cf6',
    'soul-root': '#64748b',
  },
}
```

#### Semantic Colors

```javascript
colors: {
  primary: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },
  surface: {
    canvas: '#fafaf9', // warm off-white for graph background
    panel: '#ffffff',
    elevated: '#ffffff',
    overlay: 'rgba(15, 23, 42, 0.5)',
  },
}
```

### Typography Scale

```javascript
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
  hebrew: ['Noto Serif Hebrew', 'David Libre', 'serif'],
  serif: ['Merriweather', 'Georgia', 'serif'],
},

fontSize: {
  'xs': ['0.75rem', { lineHeight: '1rem' }],
  'sm': ['0.875rem', { lineHeight: '1.25rem' }],
  'base': ['1rem', { lineHeight: '1.5rem' }],
  'lg': ['1.125rem', { lineHeight: '1.75rem' }],
  'xl': ['1.25rem', { lineHeight: '1.75rem' }],
  '2xl': ['1.5rem', { lineHeight: '2rem' }],
  '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
}
```

**Usage:**
- Graph node labels: `text-sm font-medium`
- Panel headers: `text-lg font-semibold`
- Section titles: `text-base font-semibold uppercase tracking-wide`
- Body text: `text-base leading-relaxed`
- Captions/metadata: `text-xs text-slate-500`
- Hebrew text: `font-hebrew text-lg` (increased size for readability of complex script)

### Spacing System

Based on 8px grid with 4px half-steps:

```javascript
spacing: {
  '0.5': '0.125rem',  // 2px
  '1': '0.25rem',     // 4px
  '1.5': '0.375rem',  // 6px
  '2': '0.5rem',      // 8px
  '2.5': '0.625rem',  // 10px
  '3': '0.75rem',     // 12px
  '4': '1rem',        // 16px
  '5': '1.25rem',     // 20px
  '6': '1.5rem',      // 24px
  '8': '2rem',        // 32px
  '10': '2.5rem',     // 40px
  '12': '3rem',       // 48px
  '16': '4rem',       // 64px
}
```

**Key Layout Values:**
- Top Bar height: `h-14` (56px)
- Sidebar width: `w-96` (384px) desktop, `w-80` (320px) tablet
- Node minimum padding: `p-2` (8px)
- Card padding: `p-4` (16px)
- Section gap: `gap-4` (16px)

---

## 8. Responsive Design

### Breakpoints

```javascript
screens: {
  'sm': '640px',
  'md': '768px',
  'lg': '1024px',
  'xl': '1280px',
  '2xl': '1536px',
}
```

### Mobile Layout (<768px)

**Adaptations:**
- **Top Bar:** Logo + hamburger menu + search icon (search expands to full width on focus)
- **View Switcher:** Collapsed into dropdown menu
- **Graph Canvas:** Full width, full height minus Top Bar
- **Node Detail Panel:** Full-screen modal, slide up from bottom
  - Swipe down to dismiss
  - Tab bar scrollable horizontally
- **Floating Controls:** Stacked vertically in bottom-right, 48px fab buttons
- **Layer Selector:** Bottom sheet modal
- **Touch Targets:** Minimum 44x44px for all interactive elements
- **Node Labels:** Hidden below 50% zoom; shown on tap
- **Breadcrumb:** Collapsed to "Back" button + current segment

**Graph Interactions (Touch):**
- Tap node: Select and open detail panel
- Double-tap: Zoom in to node
- Pinch: Zoom
- Pan: Single finger drag (on background)
- Long-press node: Context menu (pin, center, etc.)

### Tablet Layout (768px-1024px)

**Adaptations:**
- **Sidebar:** 320px wide, collapsible
- **Graph Canvas:** Remaining width
- **Node Detail Panel:** Sidebar on right (same as desktop but narrower)
- **Floating Controls:** Horizontal row in bottom-right
- **Layer Selector:** Floating panel, 240px wide

### Desktop Layout (>1024px)

**Default Layout:**
- **Sidebar:** 400px wide, open by default
- **Graph Canvas:** ~65% of viewport
- **Resizable:** Sidebar can be resized between 320px and 480px by dragging edge
- **Keyboard Shortcuts:**
  - `/` or `Cmd+K`: Focus search
  - `Esc`: Close panel / deselect node
  - `1-5`: Switch views
  - `+/-`: Zoom
  - `0`: Reset zoom
  - `Arrow keys`: Pan
  - `Shift + Arrow keys`: Fast pan

---

## 9. Accessibility

### WCAG 2.1 AA Compliance Strategy

#### ARIA Labels for Interactive Graph Elements

**Graph Canvas:**
- Canvas element: `role="application" aria-label="Interactive knowledge graph"`
- When a node is selected: `aria-live="polite"` region announces "Selected [Node Name], [Node Type]"
- Node count announcement on view change: "Showing 45 nodes and 78 connections"

**Nodes (SVG elements):**
- `role="button"` (nodes are clickable)
- `aria-label="[Node Name], [Node Type]. [Connection count] connections."`
- `tabindex="0"` for keyboard focusability
- Focus ring: `outline-2 outline-amber-500 outline-offset-2`

**Edges (SVG elements):**
- `role="none"` (edges are not independently focusable)
- Relationship announced via node descriptions: "Connected to [Target] via [Relationship]"

**Controls:**
- All buttons have explicit `aria-label` or visible text
- Slider: `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, `aria-label="Graph depth, 1 to 3"`
- Toggle switches: `role="switch" aria-checked="true/false"`

#### Keyboard Navigation Flow

**Global Shortcuts:**
- `Tab`: Cycle through focusable elements in Top Bar
- `Shift+Tab`: Reverse cycle
- `/`: Jump to search input
- `Escape`: Close panels, deselect node, cancel search

**Graph Navigation:**
- `Tab` (when Canvas focused): Move focus to next node in reading order (left-to-right, top-to-bottom)
- `Shift+Tab`: Previous node
- `Enter` or `Space`: Select focused node (same as click)
- `Arrow keys`: Move to nearest node in that direction (spatial navigation)
- `Home`: Focus first node
- `End`: Focus last node

**Panel Navigation:**
- `Tab`: Cycle through tabs and content
- `Arrow Left/Right`: Switch tabs when tab bar is focused
- `Escape`: Close panel (returns focus to graph canvas)

#### Focus Management

**Focus Trap (Modal):**
- When Node Detail Panel is open in modal mode on mobile, focus is trapped within the modal
- `FocusTrap` component using `focus-trap-react` or custom implementation
- First focusable element receives focus on open
- On close, focus returns to the trigger element (the node that was selected)

**Focus Restoration:**
- All focus changes are logged in React Refs
- When a panel closes, `previouslyFocusedElement.current?.focus()` is called

#### Screen Reader Announcements

**Dynamic Updates (aria-live regions):**

```
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {announcement}
</div>
```

**Announcement Patterns:**
- Node selected: "Selected Shabbat, Concept. 12 connections."
- View changed: "Switched to Person Graph View. Showing Rashi and 24 connections."
- Depth changed: "Expanded to 2 hops. Added 15 nodes."
- Filter applied: "Filtered by Person and Book types. Showing 8 of 45 nodes."
- Layer toggled: "Promises layer active. 23 nodes highlighted."
- Search results: "12 results found for 'charity'"

**Debounce:** Announcements are debounced 300ms to prevent rapid-fire updates during graph animation.

#### Color Contrast Compliance

**Minimum Contrast Ratios (4.5:1 for normal text, 3:1 for large text):**

| Element | Foreground | Background | Ratio | Pass |
|---------|-----------|------------|-------|------|
| Node label (Person) | `text-blue-900` (#1e3a8a) | `bg-blue-50` (#eff6ff) | 8.2:1 | AA |
| Node label (Book) | `text-amber-900` (#78350f) | `bg-amber-50` (#fffbeb) | 7.5:1 | AA |
| Node label (Concept) | `text-emerald-900` (#064e3b) | `bg-emerald-50` (#ecfdf5) | 7.8:1 | AA |
| Node label (Verse) | `text-violet-900` (#4c1d95) | `bg-violet-50` (#f5f3ff) | 8.5:1 | AA |
| Node label (Commentary) | `text-rose-900` (#881337) | `bg-rose-50` (#fff1f2) | 7.1:1 | AA |
| Body text | `text-slate-900` (#0f172a) | `bg-white` (#ffffff) | 12.6:1 | AA |
| Secondary text | `text-slate-500` (#64748b) | `bg-white` (#ffffff) | 5.7:1 | AA |
| Primary button | `text-white` (#ffffff) | `bg-amber-700` (#b45309) | 5.2:1 | AA |

**Colorblind Accessibility:**
- Nodes are distinguished by **shape + color + pattern**:
  - Person: Square with rounded corners, solid fill
  - Book: Square with rounded corners, book icon overlay
  - Concept: Diamond shape (rotated square)
  - Verse: Circle
  - Commentary: Circle with dashed border
- Layer accents use **pattern fills** (subtle stripes/dots) in addition to color glow
- Edge types use **stroke pattern** (solid, dashed, dotted) in addition to color

---

## 10. Performance Optimizations

### Virtualization Strategy

**Viewport Culling:**
Only nodes and edges within or near the visible viewport (+20% buffer) are rendered:

```typescript
const isInViewport = (node: GraphNode, viewport: Viewport, buffer: number = 0.2): boolean => {
  const bufferX = viewport.width * buffer;
  const bufferY = viewport.height * buffer;
  return (
    node.x >= viewport.x - bufferX &&
    node.x <= viewport.x + viewport.width + bufferX &&
    node.y >= viewport.y - bufferY &&
    node.y <= viewport.y + viewport.height + bufferY
  );
};
```

- Off-screen nodes: Not rendered, but positions simulated
- Entering viewport: Fade in over 100ms
- Exiting viewport: Fade out over 100ms

**Node Pooling:**
For Global Graph View with >500 nodes, use object pooling for DOM/SVG elements:
- Maintain a pool of 100 node elements
- Recycle elements as nodes enter/exit viewport
- Reduces GC pressure and DOM creation overhead

### Memoization Strategy

**React.memo Application Points:**

1. **GraphNode:** Memoized with custom comparison:
   ```typescript
   const GraphNode = React.memo(NodeComponent, (prev, next) => {
     return (
       prev.x === next.x &&
       prev.y === next.y &&
       prev.isSelected === next.isSelected &&
       prev.isHovered === next.isHovered &&
       prev.layerAccents.length === next.layerAccents.length
     );
   });
   ```

2. **GraphEdge:** Memoized on source/target positions and highlight state

3. **NodeLabel:** Memoized on position and zoom level (labels hidden below 0.5 zoom)

4. **NodeDetailPanel:** Memoized on `nodeId`; tab content memoized per tab

**useMemo for Computed Values:**

```typescript
const visibleNodes = useMemo(
  () => nodes.filter(n => isInViewport(n, viewport)),
  [nodes, viewport]
);

const nodeElements = useMemo(
  () => visibleNodes.map(node => <GraphNode key={node.id} {...node} />),
  [visibleNodes]
);
```

### Lazy Loading Strategy

**Graph Data:**
- Initial load: Fetch 1-hop neighborhood (fast)
- On depth increase: Fetch additional hops incrementally
- On viewport pan: Prefetch nodes in the direction of pan (low priority, abortable)
- AbortController used to cancel stale requests

**Detail Panel:**
- Panel opens immediately with skeleton UI
- Tab content loaded on demand:
  - Sources tab: Fetch on panel open
  - Connections tab: Fetch on tab activation
  - Citations tab: Fetch on tab activation
  - Related topics: Fetch on tab activation

**Images/Icons:**
- Node type icons: Inline SVG (no external requests)
- Map tiles (Person view): Lazy load when Map tab activated
- Book thumbnails: Lazy load with `loading="lazy"` or IntersectionObserver

### Rendering Technology Choice

**SVG (Default, < 1000 nodes):**
- Advantages: CSS-stylable, accessible, event-handling, sharp at all zoom levels
- Used for: Local Graph, Topic Graph, Person Graph, Book Graph

**Canvas (Fallback, 1000-5000 nodes):**
- Advantages: Better performance for many elements
- Disadvantages: Requires custom hit-testing, harder accessibility
- Implementation: Render to Canvas, maintain invisible DOM overlay for accessibility hit-testing

**WebGL (Extreme, > 5000 nodes):**
- Advantages: GPU-accelerated, handles massive graphs
- Disadvantages: Complex implementation, limited accessibility
- Reserved for: Global Graph View at very low zoom levels

**Adaptive Switching:**

```typescript
const getRendererType = (nodeCount: number): RendererType => {
  if (nodeCount < 1000) return 'svg';
  if (nodeCount < 5000) return 'canvas';
  return 'webgl';
};
```

**Transition:** When switching renderers, show a brief "Optimizing visualization..." toast.

### Animation Performance

- Use `transform` and `opacity` only (GPU-composited properties)
- Avoid animating `width`, `height`, `top`, `left`
- Graph layout simulation runs in a Web Worker to avoid blocking the main thread
- Node entrance/exit uses FLIP technique for smooth transitions
- `will-change: transform` applied to nodes during animation only, removed after

### Memory Management

- Zustand store uses Immer for immutable updates (structural sharing)
- Large graph data cached with size limits (50MB max)
- Event listeners cleaned up in `useEffect` cleanup
- ResizeObserver disconnected on unmount
- D3 simulation stopped when component unmounts (`simulation.stop()`)

---

## Appendix A: Node Type Definitions

| Type | Icon | Description | Example |
|------|------|-------------|---------|
| Person | 👤 | Historical or contemporary Torah figure | Rashi, Moses Maimonides |
| Book | 📖 | Canonical text or work | Genesis, Zohar, Tanya |
| Concept | 💡 | Abstract idea or theme | Charity, Shabbat, Teshuvah |
| Verse | 📜 | Specific biblical or textual passage | Genesis 1:1, Psalm 23 |
| Commentary | ✍️ | Explanatory text on a verse or concept | Rashi on Genesis, Tiferet Yisrael |

## Appendix B: Relationship Type Definitions

| Type | Direction | Description |
|------|-----------|-------------|
| teaches | Person → Concept/Verse | The person taught or wrote about this |
| learned from | Person → Person | The person was a student of |
| commented on | Person/Commentary → Verse/Book | Wrote commentary on |
| mentions | Any → Any | References or alludes to |
| is source for | Verse/Book → Commentary/Concept | Is the basis for |
| is promised by | Concept → Verse | The concept is promised in this verse |
| is segulah for | Concept → Concept | This concept is a remedy for |
| is tikkun for | Concept → Concept | This concept repairs |
| corresponds to | Concept → Sefirah | Maps to a sefirah |

## Appendix C: Zustand Store Schema

```typescript
// Full store type for reference
interface GraphState {
  // Data
  nodes: GraphNode[];
  edges: GraphEdge[];
  nodeMap: Map<string, GraphNode>;
  edgeMap: Map<string, GraphEdge>;
  
  // Selection
  selectedNodeId: string | null;
  hoveredNodeId: string | null;
  selectedEdgeId: string | null;
  
  // Viewport
  transform: { x: number; y: number; k: number };
  viewport: { width: number; height: number };
  
  // View
  currentView: 'local' | 'topic' | 'person' | 'book' | 'global';
  viewConfig: {
    centerNodeId?: string;
    depth?: number;
    topic?: string;
    person?: string;
    book?: string;
  };
  
  // Filters
  filters: {
    nodeTypes: NodeType[];
    relationshipTypes: RelationshipType[];
    dateRange?: [number, number];
    searchQuery?: string;
  };
  
  // Layers
  activeLayers: LayerType[];
  highlightMode: 'replace' | 'overlay' | 'dim';
  
  // Loading
  isLoading: boolean;
  loadingProgress: number;
  error: string | null;
  
  // Cache
  neighborhoodCache: LRUCache<string, { nodes: GraphNode[]; edges: GraphEdge[] }>;
}
```

---

*End of Document*
