"""RAG (Retrieval-Augmented Generation) pipeline for Torah Knowledge Graph.

Provides:
- Embedding generation for verses, concepts, commentaries
- Semantic search via Qdrant vector DB
- Context assembly for AI chat
- Citation grounding
"""

import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class SearchResult:
    score: float
    text: str
    metadata: Dict[str, Any]
    source: str  # "qdrant", "neo4j", "hybrid"


@dataclass
class RAGContext:
    question: str
    contexts: List[SearchResult]
    total_tokens: int
    sources: List[str]


class EmbeddingService:
    """Generate embeddings for Torah texts using Ollama or external API."""

    def __init__(self, provider: str = "ollama", model: str = "nomic-embed-text"):
        self.provider = provider
        self.model = model
        self._cache = {}

    async def embed(self, text: str) -> List[float]:
        """Generate embedding vector for a text."""
        cache_key = hashlib.sha256(text.encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            if self.provider == "ollama":
                import httpx
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.post(
                        "http://localhost:11434/api/embeddings",
                        json={"model": self.model, "prompt": text},
                    )
                    data = res.json()
                    embedding = data.get("embedding", [])
                    self._cache[cache_key] = embedding
                    return embedding
            else:
                # External provider (OpenAI, etc.)
                return []
        except Exception as e:
            logger.error("embedding_failed", text=text[:50], error=str(e))
            return []

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding generation."""
        results = await asyncio.gather(*[self.embed(t) for t in texts])
        return results


class QdrantSearch:
    """Semantic search via Qdrant vector database."""

    def __init__(self):
        from app.qdrant_client import qdrant_client
        self.client = qdrant_client.client
        self.collection = "torah_embeddings"

    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[SearchResult]:
        """Search Qdrant for similar vectors."""
        try:
            from qdrant_client.models import Filter

            search_filter = Filter(**filters) if filters else None

            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter,
                with_payload=True,
            )

            return [
                SearchResult(
                    score=r.score,
                    text=r.payload.get("text", ""),
                    metadata=r.payload.get("metadata", {}),
                    source="qdrant",
                )
                for r in results
            ]
        except Exception as e:
            logger.error("qdrant_search_failed", error=str(e))
            return []

    async def upsert(
        self,
        id: str,
        vector: List[float],
        text: str,
        metadata: Dict[str, Any],
    ):
        """Upsert a vector into Qdrant."""
        try:
            from qdrant_client.models import PointStruct

            self.client.upsert(
                collection_name=self.collection,
                points=[
                    PointStruct(
                        id=id,
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
        except Exception as e:
            logger.error("qdrant_upsert_failed", id=id, error=str(e))


class GraphSearch:
    """Graph-based context retrieval from Neo4j."""

    def __init__(self):
        from app.neo4j_client import neo4j_client
        self.driver = neo4j_client.driver

    async def search_verses(self, keywords: List[str], limit: int = 5) -> List[SearchResult]:
        """Search verses by keywords using full-text index."""
        try:
            query = " OR ".join(keywords)
            cypher = """
            CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $query)
            YIELD node, score
            RETURN node.ref as ref, node.hebrew as text, node.book as book,
                   node.chapter as chapter, node.verse as verse, score
            ORDER BY score DESC
            LIMIT $limit
            """

            records, _, _ = self.driver.execute_query(
                cypher, query=query, limit=limit
            )

            return [
                SearchResult(
                    score=r["score"],
                    text=r["text"] or "",
                    metadata={
                        "ref": r["ref"],
                        "book": r["book"],
                        "chapter": r["chapter"],
                        "verse": r["verse"],
                    },
                    source="neo4j",
                )
                for r in records
            ]
        except Exception as e:
            logger.error("graph_search_failed", error=str(e))
            return []

    async def get_context(self, ref: str, radius: int = 1) -> List[SearchResult]:
        """Get neighborhood context around a verse reference."""
        try:
            cypher = """
            MATCH (v:Verse {ref: $ref})
            OPTIONAL MATCH (v)-[:PART_OF]-(c:Chapter)
            OPTIONAL MATCH (c)-[:PART_OF]-(b:Book)
            OPTIONAL MATCH (v)-[:MENTIONS]-(e)
            RETURN v.hebrew as text, v.ref as ref,
                   collect(DISTINCT e.label) as entities,
                   b.title as book_title
            """

            records, _, _ = self.driver.execute_query(cypher, ref=ref)

            return [
                SearchResult(
                    score=1.0,
                    text=r["text"] or "",
                    metadata={
                        "ref": r["ref"],
                        "entities": r["entities"],
                        "book_title": r["book_title"],
                    },
                    source="neo4j_context",
                )
                for r in records
            ]
        except Exception as e:
            logger.error("context_fetch_failed", error=str(e))
            return []


class RAGPipeline:
    """Full RAG pipeline: embed -> search -> assemble -> cite."""

    def __init__(self):
        self.embedder = EmbeddingService()
        self.vector_search = QdrantSearch()
        self.graph_search = GraphSearch()

    async def answer_question(
        self,
        question: str,
        top_k: int = 5,
        use_graph: bool = True,
        use_vectors: bool = True,
    ) -> RAGContext:
        """Full RAG: retrieve context from graph + vectors, assemble with citations."""
        logger.info("rag_question", question=question[:100])

        contexts = []
        sources = []

        # 1. Vector search (semantic)
        if use_vectors:
            query_vector = await self.embedder.embed(question)
            if query_vector:
                vector_results = await self.vector_search.search(query_vector, limit=top_k)
                contexts.extend(vector_results)
                sources.append("qdrant")
                logger.info("rag_vector_results", count=len(vector_results))

        # 2. Graph search (lexical + structural)
        if use_graph:
            keywords = question.split()[:5]  # Simple keyword extraction
            graph_results = await self.graph_search.search_verses(keywords, limit=top_k)
            contexts.extend(graph_results)
            sources.append("neo4j")
            logger.info("rag_graph_results", count=len(graph_results))

        # 3. Deduplicate and rank
        seen_refs = set()
        unique_contexts = []
        for ctx in sorted(contexts, key=lambda x: x.score, reverse=True):
            ref = ctx.metadata.get("ref", ctx.text[:30])
            if ref not in seen_refs:
                seen_refs.add(ref)
                unique_contexts.append(ctx)

        # 4. Assemble context string
        context_texts = []
        total_chars = 0
        max_chars = 4000  # Token budget for context

        for ctx in unique_contexts[:top_k]:
            entry = f"[{ctx.source}] {ctx.metadata.get('ref', '')}: {ctx.text}"
            if total_chars + len(entry) > max_chars:
                break
            context_texts.append(entry)
            total_chars += len(entry)

        # 5. Return structured context
        return RAGContext(
            question=question,
            contexts=unique_contexts[:top_k],
            total_tokens=len(context_texts) * 50,  # Rough estimate
            sources=sources,
        )

    def format_for_llm(self, rag_context: RAGContext) -> str:
        """Format RAG context as LLM prompt appendix."""
        lines = [
            "You are a Torah scholar AI. Answer based ONLY on the provided sources. Cite every claim with [source: ref].",
            "",
            "Sources:",
        ]

        for ctx in rag_context.contexts:
            ref = ctx.metadata.get("ref", "unknown")
            lines.append(f"[{ctx.source}] {ref}: {ctx.text}")

        lines.append("")
        lines.append(f"Question: {rag_context.question}")
        lines.append("Answer (cite sources):")

        return "\n".join(lines)


# Global RAG instance
rag_pipeline = RAGPipeline()
