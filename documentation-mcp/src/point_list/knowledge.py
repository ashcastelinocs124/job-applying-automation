"""Knowledge graph construction from extracted points."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple

from ..settings import Config
from .analyzer import ExtractedPoint, PointType
from .builder import PointList
from ..terminology.extractor import ExtractedTerm, TermType

LOGGER = logging.getLogger(__name__)


class RelationType(Enum):
    """Types of relationships between points."""

    USES = auto()  # A uses B
    IMPLEMENTS = auto()  # A implements B
    EXTENDS = auto()  # A extends B
    RELATED_TO = auto()  # A is related to B
    EXAMPLE_OF = auto()  # A is an example of B
    PARAMETER_OF = auto()  # A is a parameter of B
    RETURNS = auto()  # A returns B
    CONTAINS = auto()  # A contains B
    # New terminology relationships
    SYNONYM_OF = auto()  # A is a synonym of B
    ANTONYM_OF = auto()  # A is an antonym of B
    TERM_DEFINITION = auto()  # A defines term B
    TERM_USAGE = auto()  # A is an usage example of term B
    TERM_CATEGORY = auto()  # A is a category containing term B
    TERM_RELATED = auto()  # A is semantically related to term B


@dataclass
class Relationship:
    """A relationship between two points."""

    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphNode:
    """A node in the knowledge graph."""

    point: ExtractedPoint
    incoming: List[Relationship] = field(default_factory=list)
    outgoing: List[Relationship] = field(default_factory=list)
    # New terminology support
    terminology_data: Optional[Dict[str, Any]] = field(default_factory=dict)
    term_embeddings: Optional[List[float]] = field(default=None)

    @property
    def degree(self) -> int:
        """Total number of connections."""
        return len(self.incoming) + len(self.outgoing)
    
    @property
    def is_terminology_node(self) -> bool:
        """Check if this node represents terminology."""
        return "term_type" in self.terminology_data


class KnowledgeGraph:
    """A graph representation of documentation knowledge.

    Nodes are ExtractedPoints, edges are Relationships.
    Enables traversal and querying of related concepts.
    Enhanced with terminology support for semantic relationships.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self._nodes: Dict[str, GraphNode] = {}
        self._relationships: List[Relationship] = []
        # New terminology support
        self._term_nodes: Dict[str, GraphNode] = {}
        self._term_index: Dict[str, str] = {}  # term name -> node id

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._relationships)

    def add_point(self, point: ExtractedPoint) -> None:
        """Add a point as a node in the graph."""
        if point.id not in self._nodes:
            self._nodes[point.id] = GraphNode(point=point)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship between two points."""
        # Ensure both nodes exist
        if relationship.source_id not in self._nodes:
            LOGGER.warning(
                "Source node %s not found for relationship",
                relationship.source_id,
            )
            return
        if relationship.target_id not in self._nodes:
            LOGGER.warning(
                "Target node %s not found for relationship",
                relationship.target_id,
            )
            return

        self._relationships.append(relationship)
        self._nodes[relationship.source_id].outgoing.append(relationship)
        self._nodes[relationship.target_id].incoming.append(relationship)

    def get_node(self, point_id: str) -> Optional[GraphNode]:
        """Get a node by its point ID."""
        return self._nodes.get(point_id)

    def get_related(
        self,
        point_id: str,
        relation_type: Optional[RelationType] = None,
        direction: str = "both",
    ) -> List[ExtractedPoint]:
        """Get points related to a given point.

        Args:
            point_id: The point to find relations for
            relation_type: Optional filter by relation type
            direction: "incoming", "outgoing", or "both"

        Returns:
            List of related points
        """
        node = self._nodes.get(point_id)
        if not node:
            return []

        related: Set[str] = set()

        if direction in ("outgoing", "both"):
            for rel in node.outgoing:
                if relation_type is None or rel.relation_type == relation_type:
                    related.add(rel.target_id)

        if direction in ("incoming", "both"):
            for rel in node.incoming:
                if relation_type is None or rel.relation_type == relation_type:
                    related.add(rel.source_id)

        return [self._nodes[pid].point for pid in related if pid in self._nodes]

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3,
    ) -> Optional[List[ExtractedPoint]]:
        """Find a path between two points using BFS."""
        if source_id not in self._nodes or target_id not in self._nodes:
            return None

        if source_id == target_id:
            return [self._nodes[source_id].point]

        visited: Set[str] = {source_id}
        queue: List[Tuple[str, List[str]]] = [(source_id, [source_id])]

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            node = self._nodes[current_id]

            for rel in node.outgoing + node.incoming:
                neighbor_id = (
                    rel.target_id if rel.source_id == current_id else rel.source_id
                )

                if neighbor_id == target_id:
                    return [self._nodes[pid].point for pid in path + [target_id]]

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    def get_central_nodes(self, limit: int = 10) -> List[ExtractedPoint]:
        """Get the most connected nodes (by degree centrality)."""
        sorted_nodes = sorted(
            self._nodes.values(),
            key=lambda n: n.degree,
            reverse=True,
        )
        return [n.point for n in sorted_nodes[:limit]]

    def from_point_list(self, point_list: PointList) -> None:
        """Populate graph from a point list."""
        # Add all points as nodes
        for point in point_list.points:
            self.add_point(point)

        # Create relationships based on pre-linked related points
        for point in point_list.points:
            for related_id in point.related_points:
                if related_id in self._nodes:
                    self.add_relationship(
                        Relationship(
                            source_id=point.id,
                            target_id=related_id,
                            relation_type=RelationType.RELATED_TO,
                            confidence=0.7,
                        )
                    )

        # Infer additional relationships
        self._infer_relationships()

    def _infer_relationships(self) -> None:
        """Infer relationships based on point types and content."""
        nodes = list(self._nodes.values())

        for node in nodes:
            point = node.point

            # Examples are EXAMPLE_OF functions/concepts
            if point.point_type == PointType.EXAMPLE:
                for other_node in nodes:
                    if other_node.point.id == point.id:
                        continue

                    other = other_node.point
                    if other.point_type in (PointType.FUNCTION, PointType.CLASS):
                        # Check if function name appears in example
                        if other.name.lower() in point.metadata.get("code", "").lower():
                            self.add_relationship(
                                Relationship(
                                    source_id=point.id,
                                    target_id=other.id,
                                    relation_type=RelationType.EXAMPLE_OF,
                                    confidence=0.8,
                                )
                            )

            # Methods/Functions may CONTAIN parameters
            if point.point_type == PointType.FUNCTION:
                params = point.metadata.get("parameters", "")
                if params:
                    # Look for parameter documentation
                    for other_node in nodes:
                        other = other_node.point
                        if other.point_type == PointType.PARAMETER:
                            if other.name.lower() in params.lower():
                                self.add_relationship(
                                    Relationship(
                                        source_id=point.id,
                                        target_id=other.id,
                                        relation_type=RelationType.PARAMETER_OF,
                                        confidence=0.7,
                                    )
                                )

    def search(
        self,
        query: str,
        limit: int = 10,
        expand_related: bool = True,
    ) -> List[ExtractedPoint]:
        """Search the knowledge graph.

        Optionally expands results to include related nodes.
        """
        query_lower = query.lower()
        scored: List[Tuple[float, ExtractedPoint]] = []

        for node in self._nodes.values():
            point = node.point
            score = 0.0

            if query_lower in point.name.lower():
                score += 1.0
            if query_lower in point.description.lower():
                score += 0.5

            # Boost by connectivity
            score += min(node.degree * 0.1, 0.3)

            if score > 0:
                scored.append((score * point.confidence, point))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [p for _, p in scored[:limit]]

        if expand_related and results:
            # Add closely related nodes not already in results
            result_ids = {p.id for p in results}
            for point in results[:3]:  # Expand top 3
                for related in self.get_related(point.id):
                    if related.id not in result_ids and len(results) < limit * 2:
                        results.append(related)
                        result_ids.add(related.id)

        return results[:limit]

    def add_terminology(self, terms: List[ExtractedTerm]) -> None:
        """Add terminology nodes to the knowledge graph."""
        for term in terms:
            # Convert ExtractedTerm to ExtractedPoint for compatibility
            point = ExtractedPoint(
                point_type=PointType.CONCEPT,  # Treat all terms as concepts initially
                name=term.term,
                description=term.definition or term.context,
                source_url=term.source_url,
                confidence=term.confidence,
                metadata={
                    **term.metadata,
                    "term_type": term.term_type.name,
                    "frequency": term.frequency,
                    "is_terminology": True,
                },
                related_points=term.related_terms,
            )
            
            # Add as a regular node
            self.add_point(point)
            
            # Store in terminology-specific indices
            node = self._nodes[point.id]
            node.terminology_data = {
                "term_type": term.term_type.name,
                "frequency": term.frequency,
                "context": term.context,
                "original_term": term.term,
            }
            
            self._term_nodes[point.id] = node
            self._term_index[term.term.lower()] = point.id
        
        # Create terminology relationships
        self._create_terminology_relationships(terms)
    
    def _create_terminology_relationships(self, terms: List[ExtractedTerm]) -> None:
        """Create relationships between terminology nodes."""
        # Group terms by source for context-aware relationships
        terms_by_source: Dict[str, List[ExtractedTerm]] = {}
        for term in terms:
            if term.source_url not in terms_by_source:
                terms_by_source[term.source_url] = []
            terms_by_source[term.source_url].append(term)
        
        for source_terms in terms_by_source.values():
            # Create relationships based on term types and context
            for i, term1 in enumerate(source_terms):
                for term2 in source_terms[i+1:]:
                    self._infer_term_relationship(term1, term2)
    
    def _infer_term_relationship(self, term1: ExtractedTerm, term2: ExtractedTerm) -> None:
        """Infer relationship between two terms based on their properties."""
        id1 = self._term_index.get(term1.term.lower())
        id2 = self._term_index.get(term2.term.lower())
        
        if not id1 or not id2:
            return
        
        # Hierarchical relationships
        if term1.term_type == TermType.CONCEPT and term2.term_type == TermType.TECHNICAL_TERM:
            if term2.term.lower() in term1.context.lower():
                self.add_relationship(Relationship(
                    source_id=id1,
                    target_id=id2,
                    relation_type=RelationType.TERM_CATEGORY,
                    confidence=0.7,
                ))
        
        elif term2.term_type == TermType.CONCEPT and term1.term_type == TermType.TECHNICAL_TERM:
            if term1.term.lower() in term2.context.lower():
                self.add_relationship(Relationship(
                    source_id=id2,
                    target_id=id1,
                    relation_type=RelationType.TERM_CATEGORY,
                    confidence=0.7,
                ))
        
        # Definition relationships
        if term1.definition and term2.term.lower() in term1.definition.lower():
            self.add_relationship(Relationship(
                source_id=id1,
                target_id=id2,
                relation_type=RelationType.TERM_DEFINITION,
                confidence=0.8,
            ))
        elif term2.definition and term1.term.lower() in term2.definition.lower():
            self.add_relationship(Relationship(
                source_id=id2,
                target_id=id1,
                relation_type=RelationType.TERM_DEFINITION,
                confidence=0.8,
            ))
        
        # Semantic relationships (based on shared context)
        if self._terms_share_context(term1, term2):
            self.add_relationship(Relationship(
                source_id=id1,
                target_id=id2,
                relation_type=RelationType.TERM_RELATED,
                confidence=0.6,
            ))
    
    def _terms_share_context(self, term1: ExtractedTerm, term2: ExtractedTerm, window: int = 50) -> bool:
        """Check if two terms appear in similar contexts."""
        context1 = term1.context.lower()
        context2 = term2.context.lower()
        
        # Check for shared words
        words1 = set(context1.split())
        words2 = set(context2.split())
        
        # Remove common words
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words1 -= common_words
        words2 -= common_words
        
        # If they share significant words, consider them related
        shared_words = words1 & words2
        return len(shared_words) >= 3
    
    def search_terminology(
        self,
        query: str,
        limit: int = 10,
        term_types: Optional[List[TermType]] = None,
        expand_related: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search specifically in terminology nodes."""
        query_lower = query.lower()
        scored: List[Tuple[float, GraphNode]] = []
        
        for node in self._term_nodes.values():
            # Filter by term types if specified
            if term_types:
                node_term_type = node.terminology_data.get("term_type", "")
                if node_term_type not in [t.name for t in term_types]:
                    continue
            
            point = node.point
            score = 0.0
            
            # Exact term match
            if query_lower == point.name.lower():
                score += 2.0
            
            # Partial term match
            elif query_lower in point.name.lower():
                score += 1.5
            
            # Description match
            elif query_lower in point.description.lower():
                score += 1.0
            
            # Context match
            elif query_lower in node.terminology_data.get("context", "").lower():
                score += 0.5
            
            # Boost by frequency
            frequency = node.terminology_data.get("frequency", 1)
            score += min(frequency * 0.1, 0.5)
            
            # Boost by connectivity
            score += min(node.degree * 0.05, 0.3)
            
            if score > 0:
                scored.append((score * point.confidence, node))
        
        # Sort and limit
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        
        for score, node in scored[:limit]:
            result = {
                "point": node.point,
                "score": score,
                "node_id": node.point.id,
                "terminology_data": node.terminology_data,
                "degree": node.degree,
            }
            
            # Add related terms if requested
            if expand_related:
                related = self.get_related(node.point.id)
                result["related_terms"] = [
                    {
                        "point": r,
                        "relationship": self._get_relationship_type(node.point.id, r.id),
                    }
                    for r in related[:5]
                ]
            
            results.append(result)
        
        return results
    
    def _get_relationship_type(self, source_id: str, target_id: str) -> Optional[str]:
        """Get the relationship type between two nodes."""
        for rel in self._relationships:
            if rel.source_id == source_id and rel.target_id == target_id:
                return rel.relation_type.name
            elif rel.source_id == target_id and rel.target_id == source_id:
                return rel.relation_type.name
        return None
    
    def get_term_hierarchy(self, term: str) -> Dict[str, Any]:
        """Get hierarchical relationships for a term."""
        term_id = self._term_index.get(term.lower())
        if not term_id:
            return {"error": f"Term '{term}' not found"}
        
        node = self.get_node(term_id)
        if not node:
            return {"error": f"Node for term '{term}' not found"}
        
        # Get parent categories
        parents = self.get_related(term_id, RelationType.TERM_CATEGORY, "incoming")
        
        # Get child terms
        children = self.get_related(term_id, RelationType.TERM_CATEGORY, "outgoing")
        
        # Get related terms
        related = self.get_related(term_id, RelationType.TERM_RELATED, "both")
        
        # Get definitions
        definitions = self.get_related(term_id, RelationType.TERM_DEFINITION, "outgoing")
        
        return {
            "term": term,
            "node_id": term_id,
            "parents": [{"name": p.name, "id": p.id} for p in parents],
            "children": [{"name": c.name, "id": c.id} for c in children],
            "related": [{"name": r.name, "id": r.id} for r in related],
            "definitions": [{"name": d.name, "id": d.id} for d in definitions],
            "total_connections": node.degree,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        return {
            "nodes": [node.point.id for node in self._nodes.values()],
            "edges": [
                {
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "type": rel.relation_type.name,
                    "confidence": rel.confidence,
                }
                for rel in self._relationships
            ],
            "stats": {
                "node_count": self.node_count,
                "edge_count": self.edge_count,
            },
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        type_counts: Dict[str, int] = {}
        for node in self._nodes.values():
            type_name = node.point.point_type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        relation_counts: Dict[str, int] = {}
        for rel in self._relationships:
            rel_name = rel.relation_type.name
            relation_counts[rel_name] = relation_counts.get(rel_name, 0) + 1

        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes_by_type": type_counts,
            "edges_by_type": relation_counts,
            "avg_degree": (
                sum(n.degree for n in self._nodes.values()) / max(1, self.node_count)
            ),
            "terminology_stats": {
                "term_nodes": len(self._term_nodes),
                "unique_terms": len(self._term_index),
            },
        }
