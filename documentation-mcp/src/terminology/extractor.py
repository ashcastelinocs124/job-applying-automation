"""AI-powered terminology extraction from documentation."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

try:  # Optional dependency for AI-powered extraction
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional runtime dependency
    OpenAI = None  # type: ignore

from ..settings import Config
from ..web_scraper import ScrapedPage

LOGGER = logging.getLogger(__name__)


class TermType(Enum):
    """Types of terminology that can be extracted."""
    
    TECHNICAL_TERM = auto()
    FUNCTION_NAME = auto()
    CLASS_NAME = auto()
    METHOD_NAME = auto()
    VARIABLE_NAME = auto()
    CONCEPT = auto()
    ACRONYM = auto()
    DOMAIN_SPECIFIC = auto()


@dataclass
class ExtractedTerm:
    """A single extracted term with metadata."""
    
    term: str
    term_type: TermType
    definition: str
    context: str
    source_url: str
    confidence: float = 0.8
    frequency: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_terms: List[str] = field(default_factory=list)
    
    @property
    def id(self) -> str:
        """Generate a unique identifier for this term."""
        term_slug = re.sub(r"[^a-z0-9]", "_", self.term.lower())[:20]
        return f"term_{term_slug}"


class TerminologyExtractor:
    """Extracts important terminology from documentation using AI and heuristics."""
    
    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.terminology
        self._llm_client = self._init_llm_client()
        
    def _init_llm_client(self):  # pragma: no cover - runtime integration
        """Initialize OpenAI client for AI-powered extraction."""
        api_key = None  # Get from config or environment
        if OpenAI is None or not api_key:
            LOGGER.info("OpenAI client unavailable; using heuristic extraction only")
            return None
        try:
            return OpenAI(api_key=api_key)
        except Exception as exc:
            LOGGER.warning("Failed to initialize OpenAI client: %s", exc)
            return None
    
    async def extract_from_page(self, page: ScrapedPage) -> List[ExtractedTerm]:
        """Extract terminology from a single documentation page."""
        terms: List[ExtractedTerm] = []
        
        # Extract using heuristics
        terms.extend(self._extract_technical_terms(page))
        terms.extend(self._extract_code_entities(page))
        terms.extend(self._extract_concepts(page))
        terms.extend(self._extract_acronyms(page))
        
        # Enhance with AI if available
        if self._llm_client:
            ai_terms = await self._extract_with_ai(page)
            terms.extend(ai_terms)
        
        # Deduplicate and rank
        terms = self._deduplicate_terms(terms)
        terms = self._rank_terms(terms)
        
        # Limit to configured maximum
        max_terms = self.settings.max_terms_per_page
        if len(terms) > max_terms:
            terms = terms[:max_terms]
        
        LOGGER.debug("Extracted %d terms from %s", len(terms), page.url)
        return terms
    
    def _extract_technical_terms(self, page: ScrapedPage) -> List[ExtractedTerm]:
        """Extract technical terms using patterns and heuristics."""
        terms: List[ExtractedTerm] = []
        content = page.markdown or page.text
        
        # Technical term patterns (capitalized words, camelCase, etc.)
        patterns = [
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b',  # PascalCase
            r'\b[a-z]+[A-Z][a-zA-Z]*\b',          # camelCase
            r'\b[a-z_]+[a-z_]+\b',                # snake_case
            r'\b[A-Z]{2,}\b',                     # Acronyms
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                term = match.group(0)
                
                # Skip common words
                if self._is_common_word(term):
                    continue
                
                # Extract context around the term
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                
                # Try to extract definition
                definition = self._extract_definition(term, context)
                
                terms.append(ExtractedTerm(
                    term=term,
                    term_type=TermType.TECHNICAL_TERM,
                    definition=definition,
                    context=context,
                    source_url=page.url,
                    confidence=0.7,
                    metadata={"extraction_method": "heuristic"}
                ))
        
        return terms
    
    def _extract_code_entities(self, page: ScrapedPage) -> List[ExtractedTerm]:
        """Extract function, class, and method names from code blocks."""
        terms: List[ExtractedTerm] = []
        content = page.markdown or page.text
        
        # Find code blocks
        code_pattern = r'```(?:[a-zA-Z0-9_+-]*)\n([\s\S]*?)```'
        for match in re.finditer(code_pattern, content):
            code = match.group(1)
            
            # Python functions and classes
            func_matches = re.finditer(r'(?:def|async def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
            for func_match in func_matches:
                name = func_match.group(1)
                entity_type = "class" if func_match.group(0).startswith("class") else "function"
                
                terms.append(ExtractedTerm(
                    term=name,
                    term_type=TermType.FUNCTION_NAME if "func" in entity_type else TermType.CLASS_NAME,
                    definition=f"{entity_type} definition",
                    context=code[max(0, func_match.start()-50):func_match.end()+50],
                    source_url=page.url,
                    confidence=0.9,
                    metadata={"language": "python", "entity_type": entity_type}
                ))
            
            # JavaScript/TypeScript functions and classes
            js_matches = re.finditer(r'(?:function|class|const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', code)
            for js_match in js_matches:
                name = js_match.group(1)
                terms.append(ExtractedTerm(
                    term=name,
                    term_type=TermType.FUNCTION_NAME,
                    definition="JavaScript/TypeScript entity",
                    context=code[max(0, js_match.start()-50):js_match.end()+50],
                    source_url=page.url,
                    confidence=0.9,
                    metadata={"language": "javascript"}
                ))
        
        return terms
    
    def _extract_concepts(self, page: ScrapedPage) -> List[ExtractedTerm]:
        """Extract conceptual terms from headings and emphasized text."""
        terms: List[ExtractedTerm] = []
        content = page.markdown or page.text
        
        # Heading patterns
        heading_pattern = r'^#{1,4}\s+(.+)$'
        lines = content.split('\n')
        
        for line in lines:
            match = re.match(heading_pattern, line)
            if match:
                concept = match.group(1).strip()
                
                # Skip generic headings
                if self._is_generic_heading(concept):
                    continue
                
                terms.append(ExtractedTerm(
                    term=concept,
                    term_type=TermType.CONCEPT,
                    definition=f"Concept: {concept}",
                    context=line,
                    source_url=page.url,
                    confidence=0.8,
                    metadata={"extraction_method": "heading"}
                ))
        
        # Bold/emphasized terms
        emphasis_pattern = r'\*\*([^*]+)\*\*'
        for match in re.finditer(emphasis_pattern, content):
            term = match.group(1).strip()
            if len(term) > 2 and not self._is_common_word(term):
                terms.append(ExtractedTerm(
                    term=term,
                    term_type=TermType.CONCEPT,
                    definition=f"Emphasized term",
                    context=content[max(0, match.start()-50):match.end()+50],
                    source_url=page.url,
                    confidence=0.6,
                    metadata={"extraction_method": "emphasis"}
                ))
        
        return terms
    
    def _extract_acronyms(self, page: ScrapedPage) -> List[ExtractedTerm]:
        """Extract acronyms and their definitions."""
        terms: List[ExtractedTerm] = []
        content = page.markdown or page.text
        
        # Acronym definition patterns: "API (Application Programming Interface)"
        acronym_pattern = r'\b([A-Z]{2,})\s*\(([^)]+)\)'
        for match in re.finditer(acronym_pattern, content):
            acronym = match.group(1)
            definition = match.group(2)
            
            terms.append(ExtractedTerm(
                term=acronym,
                term_type=TermType.ACRONYM,
                definition=definition,
                context=match.group(0),
                source_url=page.url,
                confidence=0.95,
                metadata={"full_form": definition}
            ))
        
        return terms
    
    async def _extract_with_ai(self, page: ScrapedPage) -> List[ExtractedTerm]:
        """Use AI to extract domain-specific terminology."""
        if not self._llm_client:
            return []
        
        content = (page.markdown or page.text)[:2000]  # Limit content length
        
        prompt = f"""
        Extract important technical terms, concepts, and domain-specific terminology from this documentation content.
        
        Content:
        {content}
        
        Return a JSON array of terms with:
        - term: the exact term
        - type: technical_term, concept, acronym, or domain_specific
        - definition: brief definition or explanation
        - confidence: 0.0-1.0 confidence score
        
        Focus on terms that are:
        - Specific to this domain/technology
        - Important for understanding the documentation
        - Likely to be searched for by users
        - Not common English words
        
        Limit to the 10 most important terms.
        """
        
        try:
            response = self._llm_client.chat.completions.create(
                model=self.config.ai.model,
                temperature=0.1,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": "You are a technical documentation analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            ai_data = json.loads(response.choices[0].message.content)
            
            terms: List[ExtractedTerm] = []
            for item in ai_data:
                term_type_map = {
                    "technical_term": TermType.TECHNICAL_TERM,
                    "concept": TermType.CONCEPT,
                    "acronym": TermType.ACRONYM,
                    "domain_specific": TermType.DOMAIN_SPECIFIC
                }
                
                terms.append(ExtractedTerm(
                    term=item["term"],
                    term_type=term_type_map.get(item["type"], TermType.TECHNICAL_TERM),
                    definition=item.get("definition", ""),
                    context=content[:200],
                    source_url=page.url,
                    confidence=item.get("confidence", 0.8),
                    metadata={"extraction_method": "ai"}
                ))
            
            return terms
            
        except Exception as exc:
            LOGGER.warning("AI extraction failed: %s", exc)
            return []
    
    def _deduplicate_terms(self, terms: List[ExtractedTerm]) -> List[ExtractedTerm]:
        """Remove duplicate terms and merge their information."""
        term_map: Dict[str, ExtractedTerm] = {}
        
        for term in terms:
            key = term.term.lower()
            if key in term_map:
                existing = term_map[key]
                # Merge information, keeping higher confidence
                if term.confidence > existing.confidence:
                    existing.confidence = term.confidence
                    existing.definition = term.definition or existing.definition
                existing.frequency += 1
                # Merge metadata
                existing.metadata.update(term.metadata)
            else:
                term.frequency = 1
                term_map[key] = term
        
        return list(term_map.values())
    
    def _rank_terms(self, terms: List[ExtractedTerm]) -> List[ExtractedTerm]:
        """Rank terms by importance and confidence."""
        def score_term(term: ExtractedTerm) -> float:
            base_score = term.confidence
            frequency_boost = min(term.frequency * 0.1, 0.3)
            type_boost = {
                TermType.FUNCTION_NAME: 0.2,
                TermType.CLASS_NAME: 0.2,
                TermType.ACRONYM: 0.15,
                TermType.TECHNICAL_TERM: 0.1,
                TermType.CONCEPT: 0.05,
            }.get(term.term_type, 0.0)
            
            return base_score + frequency_boost + type_boost
        
        return sorted(terms, key=score_term, reverse=True)
    
    def _is_common_word(self, word: str) -> bool:
        """Check if a word is too common to be a technical term."""
        common_words = {
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "this", "that", "these", "those", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "can", "may", "might", "must", "shall", "use", "used", "using", "example",
            "note", "important", "see", "also", "more", "like", "just", "only", "very"
        }
        return word.lower() in common_words
    
    def _is_generic_heading(self, heading: str) -> bool:
        """Check if a heading is too generic to be a concept."""
        generic_headings = {
            "introduction", "overview", "summary", "contents", "index", "see also",
            "references", "links", "related", "more information", "getting started",
            "installation", "setup", "configuration", "usage", "examples", "api reference"
        }
        return heading.lower() in generic_headings
    
    def _extract_definition(self, term: str, context: str) -> str:
        """Try to extract a definition for a term from its context."""
        # Look for definition patterns: "Term is...", "Term: ...", "Term - ..."
        definition_patterns = [
            rf'{re.escape(term)}\s*[:\-\—]\s*([^.!?]+)',
            rf'{re.escape(term)}\s+is\s+([^.!?]+)',
            rf'{re.escape(term)}\s+refers\s+to\s+([^.!?]+)',
        ]
        
        for pattern in definition_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
