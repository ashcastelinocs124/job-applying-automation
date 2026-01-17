"""Agentic Retrieval-Augmented Generation engine for documentation queries."""
from __future__ import annotations

import asyncio
import logging
import math
import os
import re
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:  # Optional dependency for richer responses
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional runtime dependency
    OpenAI = None  # type: ignore

from .content_processor import ContentProcessor, DocumentChunk
from .cache_manager import CacheManager
from .deep_search import DeepSearchOrchestrator
from .settings import Config
from .site_identifier import SiteCandidate, SiteIdentifier
from .web_scraper import WebScraper, ScrapedPage
from .terminology import TerminologyExtractor, TerminologyIndexer, TermSelector
from .point_list.knowledge import KnowledgeGraph

LOGGER = logging.getLogger(__name__)


class AgenticRAGEngine:
    """Coordinates site discovery, scraping, chunking, retrieval, and reasoning."""

    def __init__(
        self,
        config: Config,
        *,
        identifier: SiteIdentifier,
        scraper: WebScraper,
        processor: ContentProcessor,
        cache: CacheManager,
        deep_search: DeepSearchOrchestrator,
    ) -> None:
        self.config = config
        self.identifier = identifier
        self.scraper = scraper
        self.processor = processor
        self.cache = cache
        self.deep_search = deep_search
        self.max_sites = 5
        self.max_chunks = 8
        self._llm_client = self._init_llm_client()
        
        # Initialize terminology system
        self._terminology_extractor = TerminologyExtractor(config)
        self._terminology_indexer = TerminologyIndexer(config)
        self._term_selector = TermSelector(config)
        self._knowledge_graph = KnowledgeGraph(config)

    def _init_llm_client(self):  # pragma: no cover - runtime integration
        api_key = os.getenv("OPENAI_API_KEY")
        if OpenAI is None or not api_key:
            LOGGER.info("OpenAI client unavailable; falling back to template answers")
            return None
        try:
            return OpenAI(api_key=api_key)
        except Exception as exc:
            LOGGER.warning("Failed to initialize OpenAI client: %s", exc)
            return None

    async def _ensure_site_index(self, site_url: str, topic: Optional[str]) -> Tuple[List[DocumentChunk], Dict[str, Any]]:
        cache_key = self.cache.make_key("site_index", site_url)
        cached = self.cache.get(cache_key)
        if cached:
            chunks = [DocumentChunk.from_dict(chunk) for chunk in cached["chunks"]]
            return chunks, cached["metadata"]

        page = await self.scraper.scrape(site_url)
        if not page:
            return [], {}

        metadata = {
            "source_url": site_url,
            "source_title": page.title,
            "topic": topic or "",
        }
        chunks = self.processor.process_document(page.markdown, metadata)
        payload = {"chunks": [chunk.to_dict() for chunk in chunks], "metadata": metadata}
        self.cache.set(cache_key, payload)
        return chunks, metadata

    async def _gather_sites(self, query: str, limit: Optional[int] = None) -> List[SiteCandidate]:
        limit = limit or self.max_sites
        candidates = await self.identifier.identify(query, limit=limit)
        return candidates

    def _rank_chunks(
        self,
        query: str,
        chunk_sets: List[Tuple[SiteCandidate, List[DocumentChunk]]],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        top_k = top_k or self.max_chunks
        if not chunk_sets:
            return []

        query_embedding = self.processor.model.encode([query], convert_to_numpy=True)[0]
        query_norm = np.linalg.norm(query_embedding) or 1.0
        normalized_query = query_embedding / query_norm

        scored_chunks: List[Tuple[float, DocumentChunk, SiteCandidate]] = []
        for candidate, chunks in chunk_sets:
            for chunk in chunks:
                if not chunk.embedding:
                    continue
                embedding = np.array(chunk.embedding)
                denom = np.linalg.norm(embedding) or 1.0
                score = float(np.dot(normalized_query, embedding / denom))
                scored_chunks.append((score, chunk, candidate))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        top_chunks: List[Dict[str, Any]] = []
        for score, chunk, candidate in scored_chunks[:top_k]:
            top_chunks.append(
                {
                    "score": round(score, 4),
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                    "site": {
                        "title": candidate.title,
                        "url": candidate.url,
                        "confidence": candidate.confidence,
                    },
                }
            )
        return top_chunks

    async def _compose_answer(
        self,
        query: str,
        code_context: Optional[str],
        top_chunks: List[Dict[str, Any]],
    ) -> str:
        if not top_chunks:
            return "I could not find relevant documentation for this query."

        formatted_context = "\n\n".join(
            [f"Source: {chunk['site']['url']} (score {chunk['score']})\n{chunk['text']}" for chunk in top_chunks]
        )

        if self._llm_client is None:  # Simple fallback summarization
            summary_lines = ["Key findings:"]
            for chunk in top_chunks[:3]:
                summary_lines.append(f"- {chunk['text'][:180]}...")
            summary_lines.append("Sources:")
            for chunk in top_chunks[:3]:
                summary_lines.append(f"  * {chunk['site']['url']}")
            return "\n".join(summary_lines)

        prompt = (
            "You are a documentation research assistant. Use the provided context to answer the user question. "
            "Cite URLs inline. If code_context is provided, tailor the answer to it."
        )
        if code_context:
            prompt += f"\n\nCode context:\n{code_context}"

        messages = [
            {"role": "system", "content": prompt},
            {"role": "assistant", "content": "Here is the retrieved documentation context:"},
            {"role": "user", "content": formatted_context},
            {"role": "user", "content": f"Question: {query}"},
        ]

        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=self.config.ai.temperature,
                max_tokens=self.config.ai.max_tokens,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - runtime call
            LOGGER.warning("LLM generation failed: %s", exc)
            return formatted_context[:1000]

    async def search(self, query: str, code_context: Optional[str] = None) -> Dict[str, Any]:
        candidates = await self._gather_sites(query)
        chunk_sets: List[Tuple[SiteCandidate, List[DocumentChunk]]] = []
        for candidate in candidates:
            chunks, _ = await self._ensure_site_index(candidate.url, topic=query)
            if chunks:
                chunk_sets.append((candidate, chunks))

        top_chunks = self._rank_chunks(query, chunk_sets)
        answer = await self._compose_answer(query, code_context, top_chunks)

        return {
            "query": query,
            "answer": answer,
            "sources": [asdict(candidate) for candidate in candidates],
            "top_chunks": top_chunks,
        }

    async def get_site_context(self, site_url: str, topic: Optional[str] = None) -> Dict[str, Any]:
        chunks, metadata = await self._ensure_site_index(site_url, topic)
        top_chunks = self._rank_chunks(topic or "overview", [(SiteCandidate(metadata.get("source_title", "site"), site_url, "", 0.8), chunks)])
        summary = await self._compose_answer(topic or "overview", None, top_chunks)
        return {
            "site_url": site_url,
            "metadata": metadata,
            "summary": summary,
            "chunks": top_chunks,
        }

    @staticmethod
    def _extract_code_examples(text: str, language: Optional[str] = None) -> List[str]:
        pattern = r"```(?:([a-zA-Z0-9_+-]+)\n)?([\s\S]*?)```"
        matches = re.findall(pattern, text)
        examples: List[str] = []
        for lang, snippet in matches:
            lang = lang or ""
            if language and language.lower() not in lang.lower():
                continue
            examples.append(snippet.strip())
        return examples

    async def get_examples(self, query: str, language: Optional[str] = None) -> Dict[str, Any]:
        result = await self.search(query)
        examples: List[str] = []
        for chunk in result["top_chunks"]:
            examples.extend(self._extract_code_examples(chunk["text"], language))
            if len(examples) >= 5:
                break
        return {
            "query": query,
            "examples": examples[:5],
            "sources": result["sources"],
        }

    async def validate_statement(self, statement: str) -> Dict[str, Any]:
        result = await self.search(statement)
        confidence = sum(chunk["score"] for chunk in result["top_chunks"]) / (len(result["top_chunks"]) or 1)
        verdict = "supported" if confidence > 0.5 else "inconclusive"
        return {
            "statement": statement,
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "evidence": result["top_chunks"],
        }

    async def extract_and_index_terminology(self, page: ScrapedPage) -> Dict[str, Any]:
        """Extract terminology from a page and index it for search."""
        if not self.config.terminology.enabled:
            return {"status": "disabled", "terms_extracted": 0}
        
        # Extract terms from the page
        terms = await self._terminology_extractor.extract_from_page(page)
        
        if not terms:
            return {"status": "no_terms", "terms_extracted": 0}
        
        # Index terms for fast search
        collection_name = self._get_collection_name(page.url)
        index_result = await self._terminology_indexer.index_terms(terms, collection_name)
        
        # Add to knowledge graph if enabled
        if self.config.terminology.build_knowledge_graph:
            self._knowledge_graph.add_terminology(terms)
        
        LOGGER.info(
            "Extracted and indexed %d terms from %s",
            len(terms),
            page.url
        )
        
        return {
            "status": "success",
            "terms_extracted": len(terms),
            "index_path": index_result.index_path,
            "collection": collection_name,
        }
    
    def _get_collection_name(self, url: str) -> str:
        """Generate a collection name from a URL."""
        import hashlib
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc.replace(".", "_")
        path_hash = hashlib.sha256(parsed.path.encode()).hexdigest()[:8]
        return f"{domain}_{path_hash}"
    
    async def terminology_aware_search(
        self,
        query: str,
        code_context: Optional[str] = None,
        use_knowledge_graph: bool = True,
    ) -> Dict[str, Any]:
        """Enhanced search that leverages terminology extraction and knowledge graph."""
        
        # Step 1: Search terminology index via Zoekt
        term_results = await self._terminology_indexer.search_terms(
            query,
            limit=20
        )
        
        # Step 2: Use AI agent to select best terms
        if term_results and self.config.terminology.use_ai_selection:
            # Convert search results to ExtractedTerm format for selector
            candidate_terms = await self._load_terms_from_results(term_results)
            selected = await self._term_selector.select_terms(
                candidate_terms,
                query,
            )
            selected_term_names = [s.term.term for s in selected]
        else:
            selected_term_names = [r.get("file", "").split("/")[-1].replace("term_", "").replace(".md", "") for r in term_results[:5]]
        
        # Step 3: Search knowledge graph for related concepts
        kg_results = []
        if use_knowledge_graph and self._knowledge_graph.node_count > 0:
            kg_results = self._knowledge_graph.search_terminology(
                query,
                limit=10,
                expand_related=True
            )
        
        # Step 4: Perform standard RAG search
        rag_result = await self.search(query, code_context)
        
        # Step 5: Combine and rank results
        combined_result = self._combine_search_results(
            rag_result,
            term_results,
            kg_results,
            selected_term_names
        )
        
        return combined_result
    
    async def _load_terms_from_results(self, term_results: List[Dict[str, Any]]) -> List:
        """Load ExtractedTerm objects from search results."""
        from .terminology.extractor import ExtractedTerm, TermType
        
        terms = []
        for result in term_results:
            # Parse term info from the result context
            context = result.get("context", "")
            file_name = result.get("file", "")
            
            # Extract term name from first line (markdown heading)
            lines = context.split("\n")
            term_name = lines[0].replace("# ", "").strip() if lines else "unknown"
            
            terms.append(ExtractedTerm(
                term=term_name,
                term_type=TermType.TECHNICAL_TERM,
                definition="",
                context=context,
                source_url=file_name,
                confidence=result.get("score", 0.5),
            ))
        
        return terms
    
    def _combine_search_results(
        self,
        rag_result: Dict[str, Any],
        term_results: List[Dict[str, Any]],
        kg_results: List[Dict[str, Any]],
        selected_terms: List[str],
    ) -> Dict[str, Any]:
        """Combine results from RAG, terminology, and knowledge graph searches."""
        
        # Build enhanced answer with terminology context
        terminology_context = ""
        if selected_terms:
            terminology_context = f"\n\nRelevant terminology: {', '.join(selected_terms)}"
        
        kg_context = ""
        if kg_results:
            kg_terms = [r.get("point", {}).name if hasattr(r.get("point", {}), "name") else str(r) for r in kg_results[:3]]
            if kg_terms:
                kg_context = f"\n\nRelated concepts from knowledge graph: {', '.join(str(t) for t in kg_terms)}"
        
        return {
            "query": rag_result.get("query", ""),
            "answer": rag_result.get("answer", "") + terminology_context + kg_context,
            "sources": rag_result.get("sources", []),
            "top_chunks": rag_result.get("top_chunks", []),
            "terminology": {
                "selected_terms": selected_terms,
                "term_results_count": len(term_results),
            },
            "knowledge_graph": {
                "results_count": len(kg_results),
                "related_concepts": [r.get("node_id", "") for r in kg_results[:5]],
            },
        }
    
    async def get_term_hierarchy(self, term: str) -> Dict[str, Any]:
        """Get the hierarchical relationships for a term."""
        return self._knowledge_graph.get_term_hierarchy(term)
    
    async def get_terminology_stats(self) -> Dict[str, Any]:
        """Get statistics about the terminology system."""
        index_stats = self._terminology_indexer.get_index_stats()
        kg_stats = self._knowledge_graph.get_stats()
        
        return {
            "terminology_index": index_stats,
            "knowledge_graph": kg_stats,
        }
