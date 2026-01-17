"""Zoekt-based indexing system for fast terminology lookup."""

from __future__ import annotations

import hashlib
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

from ..settings import Config
from .extractor import ExtractedTerm

LOGGER = logging.getLogger(__name__)


@dataclass
class TermIndex:
    """A searchable index of terminology with Zoekt."""
    
    terms: List[ExtractedTerm]
    index_path: str
    metadata: Dict[str, Any]


class TerminologyIndexer:
    """Indexes extracted terminology using Zoekt for fast search."""
    
    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.terminology
        self.zoekt_settings = config.zoekt
        self._index_dir = Path(self.settings.index_dir).expanduser().resolve()
        self._ensure_index_dir()
        
    def _ensure_index_dir(self) -> None:
        """Create index directory if it doesn't exist."""
        self._index_dir.mkdir(parents=True, exist_ok=True)
        
    async def index_terms(self, terms: List[ExtractedTerm], collection_name: str = "terminology") -> TermIndex:
        """Index a collection of terms for fast search."""
        if not terms:
            LOGGER.warning("No terms provided for indexing")
            return TermIndex([], str(self._index_dir), {})
        
        # Create collection directory
        collection_dir = self._index_dir / collection_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        # Group terms by source URL
        terms_by_url: Dict[str, List[ExtractedTerm]] = {}
        for term in terms:
            if term.source_url not in terms_by_url:
                terms_by_url[term.source_url] = []
            terms_by_url[term.source_url].append(term)
        
        # Write term files for Zoekt indexing
        written_files = []
        for url, url_terms in terms_by_url.items():
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
            source_dir = collection_dir / url_hash
            source_dir.mkdir(parents=True, exist_ok=True)
            
            for idx, term in enumerate(url_terms):
                file_path = source_dir / f"term_{idx}.md"
                content = self._build_term_file_content(term)
                file_path.write_text(content, encoding="utf-8")
                written_files.append(str(file_path))
        
        # Create metadata
        metadata = {
            "collection": collection_name,
            "total_terms": len(terms),
            "sources": list(terms_by_url.keys()),
            "term_types": list(set(term.term_type.name for term in terms)),
            "files_created": len(written_files),
            "index_path": str(collection_dir),
        }
        
        # Trigger Zoekt indexing if enabled
        if self.zoekt_settings.enabled and written_files:
            await self._trigger_zoekt_index(collection_dir)
        
        LOGGER.info(
            "Indexed %d terms in collection '%s' (%d files)",
            len(terms),
            collection_name,
            len(written_files)
        )
        
        return TermIndex(
            terms=terms,
            index_path=str(collection_dir),
            metadata=metadata
        )
    
    def _build_term_file_content(self, term: ExtractedTerm) -> str:
        """Build markdown content for a term file."""
        content = f"""# {term.term}

**Type:** {term.term_type.name}  
**Confidence:** {term.confidence:.2f}  
**Source:** {term.source_url}

## Definition
{term.definition or "No definition available"}

## Context
{term.context}

## Metadata
```json
{{
    "term_type": "{term.term_type.name}",
    "confidence": {term.confidence},
    "frequency": {term.frequency},
    "source_url": "{term.source_url}",
    "metadata": {term.metadata}
}}
```
"""
        if term.related_terms:
            content += f"\n## Related Terms\n{', '.join(term.related_terms)}\n"
            
        return content
    
    async def _trigger_zoekt_index(self, index_path: Path) -> None:
        """Trigger Zoekt indexing for the prepared files."""
        if not self.zoekt_settings.enabled:
            return
            
        try:
            # In a real implementation, this would call Zoekt's API
            # For now, we'll simulate the indexing process
            LOGGER.info("Triggering Zoekt indexing for %s", index_path)
            
            # Simulate API call to Zoekt server
            async with aiohttp.ClientSession() as session:
                url = f"{self.zoekt_settings.server_url}/index"
                data = {
                    "path": str(index_path),
                    "name": f"terminology_{index_path.name}",
                    "repo_url": f"file://{index_path}"
                }
                
                async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        result = await response.json()
                        LOGGER.info("Zoekt indexing started: %s", result.get("job_id"))
                    else:
                        LOGGER.warning("Zoekt indexing failed: %d", response.status)
                        
        except Exception as exc:
            LOGGER.warning("Failed to trigger Zoekt indexing: %s", exc)
    
    async def search_terms(
        self,
        query: str,
        collection_name: str = "terminology",
        limit: int = 10,
        term_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for terms using Zoekt."""
        if not self.zoekt_settings.enabled:
            # Fallback to local search
            return await self._local_search(query, collection_name, limit, term_type)
        
        try:
            # Build Zoekt query
            zoekt_query = self._build_zoekt_query(query, term_type)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.zoekt_settings.server_url}/search"
                params = {
                    "q": zoekt_query,
                    "limit": limit,
                    "context": self.zoekt_settings.context_lines,
                }
                
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._process_zoekt_results(result)
                    else:
                        LOGGER.warning("Zoekt search failed: %d", response.status)
                        return await self._local_search(query, collection_name, limit, term_type)
                        
        except Exception as exc:
            LOGGER.warning("Zoekt search failed, falling back to local search: %s", exc)
            return await self._local_search(query, collection_name, limit, term_type)
    
    def _build_zoekt_query(self, query: str, term_type: Optional[str] = None) -> str:
        """Build a Zoekt query for term search."""
        query_parts = [query]
        
        if term_type:
            query_parts.append(f"file:\"term_type.*{term_type}\"")
        
        # Add file pattern to search only term files
        query_parts.append("file:\"term_*.md\"")
        
        return " ".join(query_parts)
    
    def _process_zoekt_results(self, zoekt_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Zoekt search results into term format."""
        processed_results = []
        
        for file_match in zoekt_result.get("Files", []):
            for chunk_match in file_match.get("ChunkMatches", []):
                # Extract term information from the file content and metadata
                result = {
                    "file": file_match.get("FileName", ""),
                    "score": chunk_match.get("Score", 0.0),
                    "context": chunk_match.get("Content", ""),
                    "line_ranges": chunk_match.get("LineRanges", []),
                }
                processed_results.append(result)
        
        return processed_results[:self.zoekt_settings.max_results]
    
    async def _local_search(
        self,
        query: str,
        collection_name: str,
        limit: int,
        term_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback local search when Zoekt is unavailable."""
        collection_dir = self._index_dir / collection_name
        if not collection_dir.exists():
            return []
        
        results = []
        query_lower = query.lower()
        
        # Search through all term files
        for term_file in collection_dir.rglob("term_*.md"):
            try:
                content = term_file.read_text(encoding="utf-8")
                
                # Simple text matching
                score = 0.0
                if query_lower in content.lower():
                    score += 1.0
                
                # Boost by title match
                lines = content.split('\n')
                if lines and query_lower in lines[0].lower():
                    score += 0.5
                
                # Filter by term type if specified
                if term_type and f'"term_type": "{term_type}"' not in content:
                    continue
                
                if score > 0:
                    results.append({
                        "file": str(term_file.relative_to(collection_dir)),
                        "score": score,
                        "context": content[:200] + "..." if len(content) > 200 else content,
                        "line_ranges": [[1, min(10, len(lines))]],
                    })
                    
            except Exception as exc:
                LOGGER.warning("Error reading term file %s: %s", term_file, exc)
        
        # Sort by score and limit results
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:limit]
    
    async def get_term_details(self, term_id: str, collection_name: str = "terminology") -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific term."""
        collection_dir = self._index_dir / collection_name
        if not collection_dir.exists():
            return None
        
        # Search for term file
        for term_file in collection_dir.rglob("term_*.md"):
            try:
                content = term_file.read_text(encoding="utf-8")
                
                # Parse term information from file
                lines = content.split('\n')
                if lines and term_id.lower() in lines[0].lower():
                    return {
                        "file": str(term_file.relative_to(collection_dir)),
                        "content": content,
                        "metadata": self._extract_metadata_from_content(content),
                    }
                    
            except Exception as exc:
                LOGGER.warning("Error reading term file %s: %s", term_file, exc)
        
        return None
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """Extract metadata from term file content."""
        metadata = {}
        
        # Extract JSON metadata block
        import json
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            try:
                metadata = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        return metadata
    
    def get_index_stats(self, collection_name: str = "terminology") -> Dict[str, Any]:
        """Get statistics about the terminology index."""
        collection_dir = self._index_dir / collection_name
        if not collection_dir.exists():
            return {"exists": False, "total_terms": 0, "total_files": 0}
        
        total_files = 0
        total_size = 0
        term_types = set()
        
        for file_path in collection_dir.rglob("term_*.md"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                
                # Extract term type from content
                try:
                    content = file_path.read_text(encoding="utf-8")
                    type_match = re.search(r'"term_type": "([^"]+)"', content)
                    if type_match:
                        term_types.add(type_match.group(1))
                except Exception:
                    pass
        
        return {
            "exists": True,
            "collection": collection_name,
            "path": str(collection_dir),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "term_types": list(term_types),
        }
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a terminology collection."""
        collection_dir = self._index_dir / collection_name
        if not collection_dir.exists():
            return False
        
        try:
            import shutil
            shutil.rmtree(collection_dir)
            LOGGER.info("Deleted terminology collection '%s'", collection_name)
            return True
        except Exception as exc:
            LOGGER.error("Failed to delete collection '%s': %s", collection_name, exc)
            return False
