"""Content analysis for extracting structured points from documentation."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

from ..settings import Config
from ..web_scraper import ScrapedPage

LOGGER = logging.getLogger(__name__)


class PointType(Enum):
    """Types of points that can be extracted from documentation."""

    FUNCTION = auto()
    CLASS = auto()
    METHOD = auto()
    CONCEPT = auto()
    EXAMPLE = auto()
    PARAMETER = auto()
    RETURN_VALUE = auto()
    EXCEPTION = auto()
    CONFIGURATION = auto()
    BEST_PRACTICE = auto()
    WARNING = auto()
    NOTE = auto()


@dataclass
class ExtractedPoint:
    """A single extracted point from documentation."""

    point_type: PointType
    name: str
    description: str
    source_url: str
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_points: List[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        """Generate a unique identifier for this point."""
        type_prefix = self.point_type.name.lower()[:4]
        name_slug = re.sub(r"[^a-z0-9]", "_", self.name.lower())[:20]
        return f"{type_prefix}_{name_slug}"


class ContentAnalyzer:
    """Analyzes documentation content to extract structured points.

    Extracts:
    - Function/method signatures and descriptions
    - Class definitions
    - Concepts and explanations
    - Code examples
    - Configuration options
    - Best practices and warnings
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.point_list

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    def analyze(self, page: ScrapedPage) -> List[ExtractedPoint]:
        """Analyze a page and extract all structured points."""
        if not self.enabled:
            return []

        points: List[ExtractedPoint] = []

        if self.settings.extract_functions:
            points.extend(self._extract_functions(page))

        if self.settings.extract_concepts:
            points.extend(self._extract_concepts(page))

        if self.settings.extract_examples:
            points.extend(self._extract_examples(page))

        # Always extract warnings and notes
        points.extend(self._extract_callouts(page))

        # Limit to max points per doc
        if len(points) > self.settings.max_points_per_doc:
            # Prioritize by type and confidence
            points.sort(
                key=lambda p: (
                    p.point_type in (PointType.FUNCTION, PointType.CLASS),
                    p.confidence,
                ),
                reverse=True,
            )
            points = points[: self.settings.max_points_per_doc]

        LOGGER.debug(
            "Extracted %d points from %s",
            len(points),
            page.url,
        )

        return points

    def _extract_functions(self, page: ScrapedPage) -> List[ExtractedPoint]:
        """Extract function and method definitions from documentation."""
        points: List[ExtractedPoint] = []
        content = page.markdown or page.text

        # Python function patterns
        python_pattern = r"(?:def|async def)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)"
        for match in re.finditer(python_pattern, content):
            func_name = match.group(1)
            params = match.group(2)

            # Find description (next line or nearby text)
            desc_start = match.end()
            desc_text = content[desc_start : desc_start + 200]
            description = self._extract_description(desc_text)

            points.append(
                ExtractedPoint(
                    point_type=PointType.FUNCTION,
                    name=func_name,
                    description=description,
                    source_url=page.url,
                    metadata={"parameters": params, "language": "python"},
                )
            )

        # JavaScript/TypeScript function patterns
        js_pattern = r"(?:function|const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:=\s*(?:async\s*)?\([^)]*\)\s*=>|\([^)]*\))"
        for match in re.finditer(js_pattern, content):
            func_name = match.group(1)

            desc_start = match.end()
            desc_text = content[desc_start : desc_start + 200]
            description = self._extract_description(desc_text)

            points.append(
                ExtractedPoint(
                    point_type=PointType.FUNCTION,
                    name=func_name,
                    description=description,
                    source_url=page.url,
                    metadata={"language": "javascript"},
                )
            )

        # Class definitions
        class_pattern = r"class\s+([A-Z][a-zA-Z0-9_]*)"
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)

            desc_start = match.end()
            desc_text = content[desc_start : desc_start + 300]
            description = self._extract_description(desc_text)

            points.append(
                ExtractedPoint(
                    point_type=PointType.CLASS,
                    name=class_name,
                    description=description,
                    source_url=page.url,
                )
            )

        return points

    def _extract_concepts(self, page: ScrapedPage) -> List[ExtractedPoint]:
        """Extract conceptual definitions and explanations."""
        points: List[ExtractedPoint] = []
        content = page.markdown or page.text

        # Look for heading + definition patterns
        heading_pattern = r"^#{1,3}\s+(.+)$"
        lines = content.split("\n")

        for idx, line in enumerate(lines):
            match = re.match(heading_pattern, line)
            if not match:
                continue

            heading = match.group(1).strip()

            # Skip navigation/generic headings
            if heading.lower() in ("see also", "references", "links", "contents"):
                continue

            # Get following paragraph as description
            description_lines: List[str] = []
            for next_line in lines[idx + 1 : idx + 10]:
                if next_line.startswith("#"):
                    break
                if next_line.strip():
                    description_lines.append(next_line.strip())
                    if len(description_lines) >= 3:
                        break

            description = " ".join(description_lines)
            if len(description) < 20:
                continue

            points.append(
                ExtractedPoint(
                    point_type=PointType.CONCEPT,
                    name=heading,
                    description=description[:500],
                    source_url=page.url,
                    confidence=0.7,
                )
            )

        return points

    def _extract_examples(self, page: ScrapedPage) -> List[ExtractedPoint]:
        """Extract code examples with their descriptions."""
        points: List[ExtractedPoint] = []
        content = page.markdown or page.text

        # Find code blocks with preceding descriptions
        pattern = r"```([a-zA-Z0-9_+-]*)\n([\s\S]*?)```"
        matches = list(re.finditer(pattern, content))

        for idx, match in enumerate(matches):
            language = match.group(1) or "code"
            code = match.group(2).strip()

            if not code or len(code) < 10:
                continue

            # Get preceding text as description
            start = match.start()
            preceding = content[max(0, start - 200) : start]
            lines = [l.strip() for l in preceding.split("\n") if l.strip()]
            description = lines[-1] if lines else f"Example in {language}"

            # Generate a name from the code or description
            name = self._generate_example_name(code, description, idx)

            points.append(
                ExtractedPoint(
                    point_type=PointType.EXAMPLE,
                    name=name,
                    description=description,
                    source_url=page.url,
                    metadata={
                        "language": language,
                        "code": code[:1000],
                    },
                    confidence=0.9,
                )
            )

        return points

    def _extract_callouts(self, page: ScrapedPage) -> List[ExtractedPoint]:
        """Extract warnings, notes, and best practices."""
        points: List[ExtractedPoint] = []
        content = page.markdown or page.text

        # Common callout patterns
        callout_patterns = [
            (r"(?:^|\n)(?:>\s*)?(?:\*\*)?Warning(?:\*\*)?:?\s*(.+)", PointType.WARNING),
            (r"(?:^|\n)(?:>\s*)?(?:\*\*)?Note(?:\*\*)?:?\s*(.+)", PointType.NOTE),
            (
                r"(?:^|\n)(?:>\s*)?(?:\*\*)?Tip(?:\*\*)?:?\s*(.+)",
                PointType.BEST_PRACTICE,
            ),
            (
                r"(?:^|\n)(?:>\s*)?(?:\*\*)?Best Practice(?:\*\*)?:?\s*(.+)",
                PointType.BEST_PRACTICE,
            ),
            (
                r"(?:^|\n)(?:>\s*)?(?:\*\*)?Important(?:\*\*)?:?\s*(.+)",
                PointType.WARNING,
            ),
        ]

        for pattern, point_type in callout_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                text = match.group(1).strip()
                if len(text) < 10:
                    continue

                name = f"{point_type.name.lower()}_{len(points)}"
                points.append(
                    ExtractedPoint(
                        point_type=point_type,
                        name=name,
                        description=text[:500],
                        source_url=page.url,
                        confidence=0.85,
                    )
                )

        return points

    @staticmethod
    def _extract_description(text: str) -> str:
        """Extract a clean description from nearby text."""
        # Remove code block markers
        text = re.sub(r"```[a-z]*", "", text)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Take first sentence or first 200 chars
        sentences = re.split(r"[.!?]\s+", text)
        if sentences and len(sentences[0]) > 10:
            return sentences[0][:200]
        return text[:200]

    @staticmethod
    def _generate_example_name(code: str, description: str, index: int) -> str:
        """Generate a meaningful name for a code example."""
        # Try to extract function/class name from code
        func_match = re.search(
            r"(?:def|function|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)", code
        )
        if func_match:
            return f"example_{func_match.group(1)}"

        # Use first significant word from description
        words = re.findall(r"\b([a-zA-Z]{4,})\b", description)
        if words:
            return f"example_{words[0].lower()}"

        return f"example_{index}"
