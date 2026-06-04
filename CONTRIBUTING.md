:arrow_backward: [Back to README](README.md)

# Contributing to Torah Knowledge Graph

Thank you for your interest in contributing to the world's most advanced Torah Knowledge Graph. This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Style Guides](#style-guides)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Torah Source Integrity](#torah-source-integrity)
- [Community](#community)

---

## Code of Conduct

This project is dedicated to representing Torah knowledge with the highest standards of accuracy, integrity, and respect. All contributors must adhere to these principles:

1. **Authenticity** — Only real Torah sources. No invented citations.
2. **Respect** — Torah contains sacred texts. Handle all contributions with appropriate reverence.
3. **Accuracy** — Double-check all sources before submitting.
4. **Inclusivity** — Respect all legitimate Torah traditions (Ashkenaz, Sefarad, Mizrahi, Yemenite, etc.).
5. **No Privileging** — Do not present one opinion as "correct" while dismissing others.

---

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/torah-knowledge-graph.git`
3. Set up your development environment (see [Development Setup](#development-setup))
4. Create a new branch: `git checkout -b feature/your-feature-name`
5. Make your changes
6. Test your changes
7. Commit and push
8. Open a Pull Request

---

## How to Contribute

### Areas of Contribution

#### 1. Torah Content
- Adding new concepts with proper sources
- Expanding concept definitions with additional citations
- Adding relationships between concepts
- Documenting disputes with all sides represented
- Adding aliases and cross-references

**Critical:** All Torah content contributions require:
- Exact source citations (book, chapter, verse/page)
- Hebrew text where applicable
- Authority level (Biblical, Talmudic, Rishonic, etc.)
- Confidence level (1.0 for direct quotes, lower for inferences)

#### 2. Software Development
- Backend API improvements
- Frontend graph visualization enhancements
- ETL pipeline improvements
- AI extraction model improvements
- Database schema optimizations
- Docker infrastructure

#### 3. Documentation
- Improving existing documentation
- Adding examples and tutorials
- Translating documentation to Hebrew
- Writing blog posts or articles about the project

#### 4. Testing & Quality Assurance
- Writing tests for backend endpoints
- Testing graph queries for performance
- Validating Torah content accuracy
- Reporting bugs

---

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- `uv` package manager (Python)
- `npm` (Node.js)

### Quick Setup

```bash
# Clone and enter the project
git clone https://github.com/YOUR_USERNAME/torah-knowledge-graph.git
cd torah-knowledge-graph

# Start all services
docker-compose up -d

# Verify all services are healthy
docker-compose ps

# Install frontend dependencies
cd frontend && npm install

# Install backend dependencies
cd ../backend && uv sync

# Run tests
# Backend
cd backend && uv run pytest

# Frontend
cd frontend && npm test
```

---

## Style Guides

### Python (Backend)

- Follow PEP 8
- Use type hints everywhere
- Use `async`/`await` for I/O-bound operations
- Use Pydantic v2 for all validation
- Docstrings in Google style
- Maximum line length: 100 characters (Ruff)
- Run `uv run ruff check .` before committing
- Run `uv run pyright` for type checking

```python
async def get_node_by_id(node_id: str) -> Neo4jNode:
    """Retrieve a node from Neo4j by its UUID.

    Args:
        node_id: The UUID of the node to retrieve.

    Returns:
        The Neo4jNode object if found.

    Raises:
        NodeNotFoundError: If the node does not exist.
    """
    ...
```

### TypeScript (Frontend)

- Strict TypeScript mode
- Functional components with hooks
- Use React Flow for graph canvas
- Tailwind CSS for styling
- Maximum line length: 100 characters (Prettier)
- Run `npm run lint` before committing

```typescript
interface GraphNodeProps {
  node: Neo4jNode;
  onClick: (nodeId: string) => void;
  isSelected: boolean;
}

const GraphNode: React.FC<GraphNodeProps> = ({ node, onClick, isSelected }) => {
  // ...
};
```

### Hebrew Text in Code

- Always use UTF-8 encoding
- Preserve original Hebrew spelling (do not normalize)
- Cantillation marks should be preserved when available
- RTL text should be properly handled in UI components
- Comments in Hebrew are permitted for internal notes
- External-facing documentation in English

### Neo4j Cypher

- Use parameterized queries (never string interpolation)
- Always include `LIMIT` on variable-size queries
- Use `EXPLAIN` for query performance analysis
- Create indexes before running large imports

```cypher
MATCH (v:Verse {ref: $ref})
RETURN v
LIMIT 1
```

---

## Commit Messages

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Build process, dependencies, etc.
- `content`: Torah content additions or corrections

### Scopes

- `api`: Backend API
- `graph`: Neo4j graph schema or queries
- `ui`: Frontend UI
- `viz`: Graph visualization
- `etl`: ETL pipeline
- `ai`: AI extraction service
- `ontology`: Ontology research and models
- `docs`: Documentation

### Examples

```
feat(api): add vector search endpoint for semantic queries

Implement POST /search/semantic using Qdrant embeddings.
Returns top-k similar verses with similarity scores.

Closes #123
```

```
content(ontology): add Rambam's 13 Principles as concept nodes

Add all 13 ikkarei emunah with sources from Rambam's
introduction to Perek Chelek and Hilchot Teshuvah 3.

Each principle includes:
- Canonical name and Hebrew name
- Source citation
- Disputes (Karaites, Spinoza, etc.)
- Related concepts
```

---

## Pull Request Process

1. **Update documentation** if your change affects user-facing behavior
2. **Add tests** for new functionality
3. **Update the CHANGELOG.md** under the `[Unreleased]` section
4. **Ensure all tests pass** before submitting
5. **Request review** from at least one maintainer
6. **Address review feedback** promptly
7. **Squash commits** if requested by maintainers

### PR Title Format

```
[<type>] <scope>: Brief description
```

Example: `[feat] api: add neighborhood graph query endpoint`

### PR Description Template

```markdown
## Description
Brief description of the change.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Torah content
- [ ] Refactoring

## Torah Source Integrity (if applicable)
- [ ] All sources are real and verifiable
- [ ] Exact citations included
- [ ] Hebrew text preserved
- [ ] Authority levels specified

## Testing
- [ ] Tests added/updated
- [ ] All tests pass

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

---

## Torah Source Integrity

This is the most critical section. All Torah content contributions must pass these checks:

### Source Verification Checklist

- [ ] **Book exists** — Cited book is a real Torah work
- [ ] **Location exists** — Chapter, verse, page, or daf exists in the cited work
- [ ] **Text matches** — Quoted text matches the source (within reasonable translation bounds)
- [ ] **Attribution is correct** — The cited authority actually held this position
- [ ] **Context is preserved** — The quote is not taken out of context
- [ ] **Disputes are noted** — If this opinion is disputed, note the dispute

### Prohibited Contributions

The following will be **rejected immediately**:

- Invented sources or citations
- Misattributed quotes
- Quotes taken out of context to support a false claim
- Modern fabrications presented as ancient sources
- Content from known pseudepigrapha without labeling
- AI-hallucinated sources without human validation

### Required for Torah Content PRs

Every Torah content PR must include:

1. **Source list** — All sources cited, with full bibliographic info
2. **Validation evidence** — How you verified each source
3. **Dispute disclosure** — Any known disputes about this content
4. **Authority level** — Biblical / Talmudic / Rishonic / Achronic / Modern

---

## Community

### Communication Channels

- **Issues:** Bug reports, feature requests, content corrections
- **Discussions:** General questions, ideas, community announcements
- **Wiki:** Community-contributed guides and tutorials

### Torah Scholar Network

We maintain a network of Torah scholars who validate content:

- **Validators** review AI-extracted content and new contributions
- **Experts** in specific domains (Halacha, Kabbalah, Chassidut, Musar)
- **Geographic diversity** — Ashkenaz, Sefarad, Mizrahi, Yemenite perspectives

If you are a Torah scholar interested in becoming a validator, please open an issue with the label `validator-application`.

---

## Questions?

If you have questions about contributing:

1. Check existing documentation in `/docs`
2. Search existing issues and discussions
3. Open a new issue with the `question` label

---

Thank you for contributing to the Torah Knowledge Graph. Your work helps make Torah knowledge accessible, interconnected, and preserved for future generations.

> *"Talmud Torah k'neged kulam" — Torah study is equivalent to them all.*
