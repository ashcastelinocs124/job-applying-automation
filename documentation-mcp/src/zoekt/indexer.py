"""Code extraction and Zoekt indexing workflow."""

from __future__ import annotations

import hashlib
import logging
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..settings import Config
from ..web_scraper import ScrapedPage

LOGGER = logging.getLogger(__name__)


@dataclass
class CodeBlock:
    """A code block extracted from documentation."""

    content: str
    language: str
    source_url: str
    line_start: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def hash_id(self) -> str:
        """Generate a unique hash for this code block."""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:12]
        return f"{content_hash}_{self.language}"


class ZoektIndexer:
    """Extracts code from scraped pages and prepares for Zoekt indexing.

    Zoekt typically indexes git repositories directly, but we can prepare
    documentation code blocks in a format that can be indexed.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.zoekt
        self._index_dir = Path(self.settings.index_dir).expanduser().resolve()
        self._ensure_index_dir()

    def _ensure_index_dir(self) -> None:
        """Create index directory if it doesn't exist."""
        self._index_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def extract_code_blocks(page: ScrapedPage) -> List[CodeBlock]:
        """Extract code blocks from a scraped documentation page.

        Looks for markdown code fences (```lang...```) in the content.
        """
        pattern = r"```([a-zA-Z0-9_+-]*)\n([\s\S]*?)```"
        blocks: List[CodeBlock] = []

        # Search in markdown content
        content = page.markdown or page.text
        matches = re.finditer(pattern, content)

        for idx, match in enumerate(matches):
            language = match.group(1).lower() or "text"
            code_content = match.group(2).strip()

            if not code_content:
                continue

            # Estimate line number based on position in content
            line_start = content[: match.start()].count("\n") + 1

            blocks.append(
                CodeBlock(
                    content=code_content,
                    language=language,
                    source_url=page.url,
                    line_start=line_start,
                    metadata={
                        "source_title": page.title,
                        "block_index": str(idx),
                    },
                )
            )

        return blocks

    def prepare_for_indexing(
        self,
        blocks: List[CodeBlock],
        repo_name: str = "documentation",
    ) -> Path:
        """Prepare code blocks as files for Zoekt indexing.

        Creates a temporary directory structure that Zoekt can index:
        repo_name/
          source_url_hash/
            block_0.py
            block_1.js
            ...

        Returns the path to the prepared directory.
        """
        repo_dir = self._index_dir / repo_name
        repo_dir.mkdir(parents=True, exist_ok=True)

        # Group blocks by source URL
        blocks_by_url: Dict[str, List[CodeBlock]] = {}
        for block in blocks:
            url_hash = hashlib.sha256(block.source_url.encode()).hexdigest()[:8]
            if url_hash not in blocks_by_url:
                blocks_by_url[url_hash] = []
            blocks_by_url[url_hash].append(block)

        # Write each block to a file
        for url_hash, url_blocks in blocks_by_url.items():
            source_dir = repo_dir / url_hash
            source_dir.mkdir(parents=True, exist_ok=True)

            for idx, block in enumerate(url_blocks):
                extension = self._language_to_extension(block.language)
                file_path = source_dir / f"block_{idx}{extension}"

                # Write with metadata header
                header = self._build_metadata_header(block)
                file_content = f"{header}\n{block.content}"

                file_path.write_text(file_content, encoding="utf-8")

        return repo_dir

    @staticmethod
    def _language_to_extension(language: str) -> str:
        """Map language identifier to file extension."""
        extensions = {
            "python": ".py",
            "py": ".py",
            "javascript": ".js",
            "js": ".js",
            "typescript": ".ts",
            "ts": ".ts",
            "tsx": ".tsx",
            "jsx": ".jsx",
            "rust": ".rs",
            "go": ".go",
            "java": ".java",
            "c": ".c",
            "cpp": ".cpp",
            "c++": ".cpp",
            "csharp": ".cs",
            "cs": ".cs",
            "ruby": ".rb",
            "php": ".php",
            "swift": ".swift",
            "kotlin": ".kt",
            "scala": ".scala",
            "html": ".html",
            "css": ".css",
            "scss": ".scss",
            "json": ".json",
            "yaml": ".yaml",
            "yml": ".yaml",
            "toml": ".toml",
            "xml": ".xml",
            "sql": ".sql",
            "shell": ".sh",
            "bash": ".sh",
            "sh": ".sh",
            "zsh": ".sh",
            "fish": ".fish",
            "powershell": ".ps1",
            "dockerfile": ".dockerfile",
            "makefile": ".makefile",
            "markdown": ".md",
            "md": ".md",
            "text": ".txt",
        }
        return extensions.get(language.lower(), ".txt")

    @staticmethod
    def _build_metadata_header(block: CodeBlock) -> str:
        """Build a comment header with metadata for the code block."""
        lines = [
            f"# Source: {block.source_url}",
            f"# Title: {block.metadata.get('source_title', 'Unknown')}",
            f"# Language: {block.language}",
            f"# Original Line: {block.line_start}",
        ]
        return "\n".join(lines) + "\n"

    async def index_pages(
        self,
        pages: List[ScrapedPage],
        repo_name: str = "documentation",
    ) -> Dict[str, Any]:
        """Extract and prepare code from multiple pages for indexing.

        Returns statistics about the indexing operation.
        """
        all_blocks: List[CodeBlock] = []

        for page in pages:
            blocks = self.extract_code_blocks(page)
            all_blocks.extend(blocks)
            LOGGER.debug(
                "Extracted %d code blocks from %s",
                len(blocks),
                page.url,
            )

        if not all_blocks:
            LOGGER.info("No code blocks found in %d pages", len(pages))
            return {
                "status": "empty",
                "pages_processed": len(pages),
                "blocks_extracted": 0,
            }

        # Prepare files for Zoekt
        repo_path = self.prepare_for_indexing(all_blocks, repo_name)

        LOGGER.info(
            "Prepared %d code blocks for indexing in %s",
            len(all_blocks),
            repo_path,
        )

        return {
            "status": "prepared",
            "repo_path": str(repo_path),
            "pages_processed": len(pages),
            "blocks_extracted": len(all_blocks),
            "languages": list({block.language for block in all_blocks}),
        }

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index directory."""
        if not self._index_dir.exists():
            return {"exists": False, "total_files": 0, "total_size_bytes": 0}

        total_files = 0
        total_size = 0

        for file_path in self._index_dir.rglob("*"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size

        return {
            "exists": True,
            "path": str(self._index_dir),
            "total_files": total_files,
            "total_size_bytes": total_size,
        }
