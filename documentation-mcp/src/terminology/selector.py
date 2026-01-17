"""AI agent for intelligent term selection and shortlisting."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:  # Optional dependency for AI-powered selection
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional runtime dependency
    OpenAI = None  # type: ignore

from ..settings import Config
from .extractor import ExtractedTerm

LOGGER = logging.getLogger(__name__)


@dataclass
class SelectionCriteria:
    """Criteria for term selection."""
    
    query_relevance: float = 0.7  # Minimum relevance score to query
    confidence_threshold: float = 0.6  # Minimum term confidence
    max_results: int = 10  # Maximum number of terms to return
    diversity_threshold: float = 0.3  # Minimum semantic diversity
    boost_frequent_terms: bool = True  # Boost frequently occurring terms


@dataclass
class SelectedTerm:
    """A term that has been selected by the AI agent."""
    
    term: ExtractedTerm
    relevance_score: float
    selection_reason: str
    rank: int
    metadata: Dict[str, Any]


class TermSelector:
    """AI agent for intelligent term selection and shortlisting."""
    
    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.terminology
        self._llm_client = self._init_llm_client()
    
    def _init_llm_client(self):  # pragma: no cover - runtime integration
        """Initialize OpenAI client for AI-powered selection."""
        api_key = None  # Get from config or environment
        if OpenAI is None or not api_key:
            LOGGER.info("OpenAI client unavailable; using heuristic selection only")
            return None
        try:
            return OpenAI(api_key=api_key)
        except Exception as exc:
            LOGGER.warning("Failed to initialize OpenAI client: %s", exc)
            return None
    
    async def select_terms(
        self,
        terms: List[ExtractedTerm],
        query: str,
        criteria: Optional[SelectionCriteria] = None
    ) -> List[SelectedTerm]:
        """Select the most relevant terms for a given query."""
        if not terms:
            return []
        
        criteria = criteria or SelectionCriteria()
        
        # Filter terms by basic criteria
        filtered_terms = self._filter_terms(terms, criteria)
        
        if not filtered_terms:
            return []
        
        # Score terms for relevance
        scored_terms = await self._score_terms(filtered_terms, query)
        
        # Apply diversity filtering
        diverse_terms = self._ensure_diversity(scored_terms, criteria)
        
        # Rank and limit results
        ranked_terms = self._rank_terms(diverse_terms, criteria)
        
        # Generate selection reasons
        selected_terms = await self._generate_selection_reasons(ranked_terms, query)
        
        LOGGER.debug(
            "Selected %d terms from %d candidates for query: %s",
            len(selected_terms),
            len(terms),
            query[:50]
        )
        
        return selected_terms
    
    def _filter_terms(self, terms: List[ExtractedTerm], criteria: SelectionCriteria) -> List[ExtractedTerm]:
        """Filter terms based on basic criteria."""
        filtered = []
        
        for term in terms:
            # Confidence threshold
            if term.confidence < criteria.confidence_threshold:
                continue
            
            # Minimum frequency (optional)
            if hasattr(criteria, 'min_frequency') and term.frequency < criteria.min_frequency:
                continue
            
            filtered.append(term)
        
        return filtered
    
    async def _score_terms(self, terms: List[ExtractedTerm], query: str) -> List[tuple[ExtractedTerm, float]]:
        """Score terms based on relevance to the query."""
        if self._llm_client:
            return await self._ai_score_terms(terms, query)
        else:
            return self._heuristic_score_terms(terms, query)
    
    async def _ai_score_terms(self, terms: List[ExtractedTerm], query: str) -> List[tuple[ExtractedTerm, float]]:
        """Use AI to score term relevance."""
        # Limit terms to avoid token limits
        scored_terms = []
        batch_size = 10
        
        for i in range(0, len(terms), batch_size):
            batch = terms[i:i + batch_size]
            batch_scores = await self._score_batch_with_ai(batch, query)
            scored_terms.extend(batch_scores)
        
        return scored_terms
    
    async def _score_batch_with_ai(self, terms: List[ExtractedTerm], query: str) -> List[tuple[ExtractedTerm, float]]:
        """Score a batch of terms using AI."""
        if not self._llm_client:
            return self._heuristic_score_terms(terms, query)
        
        # Prepare term descriptions for AI
        term_descriptions = []
        for term in terms:
            desc = f"Term: {term.term}\n"
            desc += f"Type: {term.term_type.name}\n"
            desc += f"Definition: {term.definition}\n"
            desc += f"Context: {term.context[:200]}...\n"
            term_descriptions.append(desc)
        
        prompt = f"""
        Score the relevance of each term to the query: "{query}"
        
        Terms to evaluate:
        {chr(10).join(f"{i+1}. {desc}" for i, desc in enumerate(term_descriptions))}
        
        Return a JSON array of scores (0.0-1.0) where:
        - 1.0 = highly relevant to the query
        - 0.5 = somewhat relevant
        - 0.0 = not relevant
        
        Consider:
        - Semantic relevance to the query
        - Technical specificity
        - Likely user intent
        - Context appropriateness
        
        Example response: [0.9, 0.3, 0.8, 0.1]
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=0.1,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": "You are a technical relevance scoring expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            scores = json.loads(response.choices[0].message.content)
            
            # Ensure we have the right number of scores
            if len(scores) != len(terms):
                LOGGER.warning("AI returned %d scores for %d terms", len(scores), len(terms))
                scores = scores[:len(terms)] + [0.5] * max(0, len(terms) - len(scores))
            
            return list(zip(terms, scores))
            
        except Exception as exc:
            LOGGER.warning("AI scoring failed: %s", exc)
            return self._heuristic_score_terms(terms, query)
    
    def _heuristic_score_terms(self, terms: List[ExtractedTerm], query: str) -> List[tuple[ExtractedTerm, float]]:
        """Score terms using heuristics."""
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        scored_terms = []
        for term in terms:
            score = 0.0
            
            # Exact term match
            if term.term.lower() == query_lower:
                score += 1.0
            
            # Partial term match
            elif query_lower in term.term.lower() or term.term.lower() in query_lower:
                score += 0.8
            
            # Query term matches in term name
            for q_term in query_terms:
                if q_term in term.term.lower():
                    score += 0.4
            
            # Query term matches in definition
            if term.definition:
                for q_term in query_terms:
                    if q_term in term.definition.lower():
                        score += 0.2
            
            # Query term matches in context
            if term.context:
                for q_term in query_terms:
                    if q_term in term.context.lower():
                        score += 0.1
            
            # Boost by confidence
            score *= term.confidence
            
            # Boost by frequency
            score *= (1 + min(term.frequency * 0.1, 0.5))
            
            # Boost by term type
            type_boost = {
                "FUNCTION_NAME": 0.2,
                "CLASS_NAME": 0.2,
                "TECHNICAL_TERM": 0.15,
                "ACRONYM": 0.1,
                "CONCEPT": 0.05,
            }.get(term.term_type.name, 0.0)
            score += type_boost
            
            scored_terms.append((term, min(score, 1.0)))
        
        return scored_terms
    
    def _ensure_diversity(
        self,
        scored_terms: List[tuple[ExtractedTerm, float]],
        criteria: SelectionCriteria
    ) -> List[tuple[ExtractedTerm, float]]:
        """Ensure semantic diversity in selected terms."""
        if len(scored_terms) <= criteria.max_results:
            return scored_terms
        
        # Sort by score
        scored_terms.sort(key=lambda x: x[1], reverse=True)
        
        # Simple diversity: avoid selecting too many terms of the same type
        diverse_terms = []
        type_counts = {}
        
        for term, score in scored_terms:
            term_type = term.term_type.name
            
            # Check type diversity
            max_per_type = max(1, criteria.max_results // 3)  # Max 1/3 of results per type
            if type_counts.get(term_type, 0) >= max_per_type:
                continue
            
            diverse_terms.append((term, score))
            type_counts[term_type] = type_counts.get(term_type, 0) + 1
            
            if len(diverse_terms) >= criteria.max_results:
                break
        
        # If we didn't get enough diverse terms, fill with top remaining
        if len(diverse_terms) < criteria.max_results:
            remaining = [t for t in scored_terms if t not in diverse_terms]
            diverse_terms.extend(remaining[:criteria.max_results - len(diverse_terms)])
        
        return diverse_terms
    
    def _rank_terms(
        self,
        scored_terms: List[tuple[ExtractedTerm, float]],
        criteria: SelectionCriteria
    ) -> List[tuple[ExtractedTerm, float]]:
        """Rank terms and apply final limits."""
        # Sort by score (descending)
        scored_terms.sort(key=lambda x: x[1], reverse=True)
        
        # Apply limit
        return scored_terms[:criteria.max_results]
    
    async def _generate_selection_reasons(
        self,
        ranked_terms: List[tuple[ExtractedTerm, float]],
        query: str
    ) -> List[SelectedTerm]:
        """Generate human-readable reasons for term selection."""
        selected_terms = []
        
        if self._llm_client:
            selected_terms = await self._generate_ai_reasons(ranked_terms, query)
        else:
            selected_terms = self._generate_heuristic_reasons(ranked_terms, query)
        
        return selected_terms
    
    async def _generate_ai_reasons(
        self,
        ranked_terms: List[tuple[ExtractedTerm, float]],
        query: str
    ) -> List[SelectedTerm]:
        """Generate selection reasons using AI."""
        if not self._llm_client:
            return self._generate_heuristic_reasons(ranked_terms, query)
        
        # Prepare for AI analysis
        term_summaries = []
        for i, (term, score) in enumerate(ranked_terms):
            summary = f"{i+1}. {term.term} (score: {score:.2f}) - {term.term_type.name}"
            term_summaries.append(summary)
        
        prompt = f"""
        For each selected term, provide a brief reason why it was chosen for the query: "{query}"
        
        Selected terms:
        {chr(10).join(term_summaries)}
        
        Return a JSON array of strings, each explaining why the corresponding term was selected.
        Keep explanations concise (1-2 sentences).
        
        Example response: [
            "Direct match for the query term",
            "Highly relevant technical concept in this domain",
            "Frequently used function related to the query"
        ]
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=0.3,
                max_tokens=800,
                messages=[
                    {"role": "system", "content": "You are a technical relevance explanation expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            reasons = json.loads(response.choices[0].message.content)
            
            # Ensure we have the right number of reasons
            if len(reasons) != len(ranked_terms):
                reasons = reasons[:len(ranked_terms)] + ["Selected by relevance scoring"] * max(0, len(ranked_terms) - len(reasons))
            
            selected_terms = []
            for i, (term, score) in enumerate(ranked_terms):
                selected_terms.append(SelectedTerm(
                    term=term,
                    relevance_score=score,
                    selection_reason=reasons[i] if i < len(reasons) else "Selected by relevance scoring",
                    rank=i + 1,
                    metadata={"selection_method": "ai"}
                ))
            
            return selected_terms
            
        except Exception as exc:
            LOGGER.warning("AI reason generation failed: %s", exc)
            return self._generate_heuristic_reasons(ranked_terms, query)
    
    def _generate_heuristic_reasons(
        self,
        ranked_terms: List[tuple[ExtractedTerm, float]],
        query: str
    ) -> List[SelectedTerm]:
        """Generate selection reasons using heuristics."""
        selected_terms = []
        query_lower = query.lower()
        
        for i, (term, score) in enumerate(ranked_terms):
            reason_parts = []
            
            # Exact match
            if term.term.lower() == query_lower:
                reason_parts.append("Exact match for query")
            
            # Partial match
            elif query_lower in term.term.lower():
                reason_parts.append("Contains query term")
            
            # High confidence
            elif term.confidence > 0.8:
                reason_parts.append("High confidence extraction")
            
            # Frequent term
            elif term.frequency > 3:
                reason_parts.append("Frequently occurring term")
            
            # Type-specific reasons
            if term.term_type.name == "FUNCTION_NAME":
                reason_parts.append("Function definition")
            elif term.term_type.name == "CLASS_NAME":
                reason_parts.append("Class definition")
            elif term.term_type.name == "ACRONYM":
                reason_parts.append("Technical acronym")
            elif term.term_type.name == "CONCEPT":
                reason_parts.append("Key concept")
            
            # Default reason
            if not reason_parts:
                reason_parts.append("Relevant to query")
            
            selected_terms.append(SelectedTerm(
                term=term,
                relevance_score=score,
                selection_reason="; ".join(reason_parts),
                rank=i + 1,
                metadata={"selection_method": "heuristic"}
            ))
        
        return selected_terms
    
    async def get_similar_terms(
        self,
        target_term: ExtractedTerm,
        all_terms: List[ExtractedTerm],
        limit: int = 5
    ) -> List[ExtractedTerm]:
        """Find terms similar to a target term."""
        if self._llm_client:
            return await self._find_similar_with_ai(target_term, all_terms, limit)
        else:
            return self._find_similar_heuristic(target_term, all_terms, limit)
    
    async def _find_similar_with_ai(
        self,
        target_term: ExtractedTerm,
        all_terms: List[ExtractedTerm],
        limit: int
    ) -> List[ExtractedTerm]:
        """Use AI to find similar terms."""
        if not self._llm_client:
            return self._find_similar_heuristic(target_term, all_terms, limit)
        
        # Exclude the target term itself
        candidate_terms = [t for t in all_terms if t.term != target_term.term]
        
        if not candidate_terms:
            return []
        
        # Prepare candidates for AI (limit to avoid token issues)
        candidates = candidate_terms[:20]
        candidate_descriptions = []
        
        for term in candidates:
            desc = f"{term.term} ({term.term_type.name}): {term.definition}"
            candidate_descriptions.append(desc)
        
        prompt = f"""
        Find terms most similar to: "{target_term.term}" - {target_term.definition}
        
        Candidate terms:
        {chr(10).join(f"{i+1}. {desc}" for i, desc in enumerate(candidate_descriptions))}
        
        Return a JSON array of indices (0-based) for the {limit} most similar terms.
        Consider semantic similarity, technical domain, and functional relationships.
        
        Example response: [2, 5, 1, 8, 0]
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=0.1,
                max_tokens=200,
                messages=[
                    {"role": "system", "content": "You are a technical similarity expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            indices = json.loads(response.choices[0].message.content)
            
            similar_terms = []
            for idx in indices[:limit]:
                if 0 <= idx < len(candidates):
                    similar_terms.append(candidates[idx])
            
            return similar_terms
            
        except Exception as exc:
            LOGGER.warning("AI similarity search failed: %s", exc)
            return self._find_similar_heuristic(target_term, all_terms, limit)
    
    def _find_similar_heuristic(
        self,
        target_term: ExtractedTerm,
        all_terms: List[ExtractedTerm],
        limit: int
    ) -> List[ExtractedTerm]:
        """Find similar terms using heuristics."""
        candidates = [t for t in all_terms if t.term != target_term.term]
        
        scored_candidates = []
        target_lower = target_term.term.lower()
        target_words = set(target_lower.split())
        
        for candidate in candidates:
            score = 0.0
            candidate_lower = candidate.term.lower()
            candidate_words = set(candidate_lower.split())
            
            # Word overlap
            word_overlap = len(target_words & candidate_words)
            if word_overlap > 0:
                score += word_overlap * 0.3
            
            # Same type
            if candidate.term_type == target_term.term_type:
                score += 0.2
            
            # Similar length (indicates similar complexity)
            length_diff = abs(len(target_lower) - len(candidate_lower))
            if length_diff <= 3:
                score += 0.1
            
            # Same source URL (contextual similarity)
            if candidate.source_url == target_term.source_url:
                score += 0.1
            
            # Substring similarity
            if target_lower in candidate_lower or candidate_lower in target_lower:
                score += 0.2
            
            scored_candidates.append((candidate, score))
        
        # Sort by score and return top results
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return [term for term, _ in scored_candidates[:limit]]
