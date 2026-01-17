"""Point list construction from analyzed content."""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..settings import Config
from ..web_scraper import ScrapedPage
from .analyzer import ContentAnalyzer, ExtractedPoint, PointType

LOGGER = logging.getLogger(__name__)


@dataclass
class PointList:
    """A collection of extracted points from documentation."""

    source_url: str
    source_title: str
    points: List[ExtractedPoint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Generate a unique identifier for this point list."""
        url_hash = hashlib.sha256(self.source_url.encode()).hexdigest()[:12]
        return f"pl_{url_hash}"

    def get_points_by_type(self, point_type: PointType) -> List[ExtractedPoint]:
        """Filter points by type."""
        return [p for p in self.points if p.point_type == point_type]

    def get_functions(self) -> List[ExtractedPoint]:
        """Get all function points."""
        return [
            p
            for p in self.points
            if p.point_type in (PointType.FUNCTION, PointType.METHOD)
        ]

    def get_classes(self) -> List[ExtractedPoint]:
        """Get all class points."""
        return self.get_points_by_type(PointType.CLASS)

    def get_examples(self) -> List[ExtractedPoint]:
        """Get all example points."""
        return self.get_points_by_type(PointType.EXAMPLE)

    def get_concepts(self) -> List[ExtractedPoint]:
        """Get all concept points."""
        return self.get_points_by_type(PointType.CONCEPT)

    def search(self, query: str, limit: int = 10) -> List[ExtractedPoint]:
        """Simple text search across points."""
        query_lower = query.lower()
        scored: List[tuple[float, ExtractedPoint]] = []

        for point in self.points:
            score = 0.0

            # Name match is high value
            if query_lower in point.name.lower():
                score += 1.0

            # Description match
            if query_lower in point.description.lower():
                score += 0.5

            # Metadata matches
            for key, value in point.metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 0.3

            if score > 0:
                scored.append((score * point.confidence, point))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:limit]]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "metadata": self.metadata,
            "points": [
                {
                    "id": p.id,
                    "type": p.point_type.name,
                    "name": p.name,
                    "description": p.description,
                    "source_url": p.source_url,
                    "confidence": p.confidence,
                    "metadata": p.metadata,
                    "related_points": p.related_points,
                }
                for p in self.points
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PointList":
        """Deserialize from dictionary."""
        points = []
        for p_data in data.get("points", []):
            points.append(
                ExtractedPoint(
                    point_type=PointType[p_data["type"]],
                    name=p_data["name"],
                    description=p_data["description"],
                    source_url=p_data["source_url"],
                    confidence=p_data.get("confidence", 0.8),
                    metadata=p_data.get("metadata", {}),
                    related_points=p_data.get("related_points", []),
                )
            )

        return cls(
            source_url=data["source_url"],
            source_title=data["source_title"],
            points=points,
            metadata=data.get("metadata", {}),
        )


class PointListBuilder:
    """Builds point lists from scraped documentation pages."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.analyzer = ContentAnalyzer(config)
        self._cache: Dict[str, PointList] = {}

    @property
    def enabled(self) -> bool:
        return self.config.point_list.enabled

    def build(self, page: ScrapedPage) -> PointList:
        """Build a point list from a scraped page."""
        if not self.enabled:
            return PointList(
                source_url=page.url,
                source_title=page.title,
            )

        # Check cache
        cache_key = page.url
        if cache_key in self._cache:
            LOGGER.debug("Using cached point list for %s", page.url)
            return self._cache[cache_key]

        # Extract points using analyzer
        points = self.analyzer.analyze(page)

        # Build point list
        point_list = PointList(
            source_url=page.url,
            source_title=page.title,
            points=points,
            metadata={
                "word_count": len(page.text.split()),
                "link_count": len(page.links),
            },
        )

        # Link related points
        if self.config.point_list.build_relationships:
            self._link_related_points(point_list)

        # Cache the result
        self._cache[cache_key] = point_list

        LOGGER.info(
            "Built point list for %s: %d points",
            page.url,
            len(points),
        )

        return point_list

    def build_many(self, pages: List[ScrapedPage]) -> List[PointList]:
        """Build point lists from multiple pages."""
        return [self.build(page) for page in pages]

    def _link_related_points(self, point_list: PointList) -> None:
        """Find and link related points within a point list."""
        points = point_list.points

        for i, point in enumerate(points):
            related: Set[str] = set()

            for j, other in enumerate(points):
                if i == j:
                    continue

                # Check for name overlap
                if point.name.lower() in other.description.lower():
                    related.add(other.id)

                # Check for common concepts
                point_words = set(point.name.lower().split())
                other_words = set(other.name.lower().split())
                if point_words & other_words:
                    related.add(other.id)

            point.related_points = list(related)[:5]  # Limit to 5 related

    def merge_point_lists(self, point_lists: List[PointList]) -> PointList:
        """Merge multiple point lists into one."""
        if not point_lists:
            return PointList(source_url="", source_title="Merged")

        merged = PointList(
            source_url="merged",
            source_title="Merged Documentation",
            metadata={"source_count": len(point_lists)},
        )

        seen_ids: Set[str] = set()
        for pl in point_lists:
            for point in pl.points:
                if point.id not in seen_ids:
                    merged.points.append(point)
                    seen_ids.add(point.id)

        return merged

    def get_stats(self) -> Dict[str, Any]:
        """Get builder statistics."""
        total_points = sum(len(pl.points) for pl in self._cache.values())
        type_counts: Dict[str, int] = {}

        for pl in self._cache.values():
            for point in pl.points:
                type_name = point.point_type.name
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "enabled": self.enabled,
            "cached_pages": len(self._cache),
            "total_points": total_points,
            "points_by_type": type_counts,
        }

    def clear_cache(self) -> None:
        """Clear the builder cache."""
        self._cache.clear()
