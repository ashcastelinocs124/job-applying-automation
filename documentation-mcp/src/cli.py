#!/usr/bin/env python3
"""
Documentation Chat CLI - Interactive terminal for exploring documentation.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console as RichConsole

RICH_AVAILABLE = False

try:
    import rich  # noqa: F401
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.box import ROUNDED
    from rich.align import Align
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.rule import Rule
    from rich.theme import Theme

    RICH_AVAILABLE = True
except ImportError:
    Console = None  # type: ignore[misc, assignment]
    Panel = None  # type: ignore[misc, assignment]
    Table = None  # type: ignore[misc, assignment]
    Markdown = None  # type: ignore[misc, assignment]
    Text = None  # type: ignore[misc, assignment]
    ROUNDED = None  # type: ignore[misc, assignment]
    Align = None  # type: ignore[misc, assignment]
    Progress = None  # type: ignore[misc, assignment]
    SpinnerColumn = None  # type: ignore[misc, assignment]
    TextColumn = None  # type: ignore[misc, assignment]
    BarColumn = None  # type: ignore[misc, assignment]
    Rule = None  # type: ignore[misc, assignment]
    Theme = None  # type: ignore[misc, assignment]

from .settings import load_config, Config, ConfigError
from .documentation_loader import DocumentationLoader, LoadedDocumentation, LoadMethod
from .web_scraper import WebScraper
from .site_identifier import SiteIdentifier
from .agentic_rag import AgenticRAGEngine
from .cache_manager import CacheManager
from .content_processor import ContentProcessor
from .deep_search import DeepSearchOrchestrator

LOGGER = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# THEME CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THEME_DICT = {
    "title": "bold #E0B0FF",
    "subtitle": "italic #A0A0A0",
    "accent": "#7EB6FF",
    "accent2": "#FFB86C",
    "success": "#98C379",
    "error": "#E06C75",
    "warning": "#E5C07B",
    "info": "#61AFEF",
    "muted": "#5C6370",
    "highlight": "#C678DD",
    "command": "#98C379",
    "url": "#61AFEF underline",
    "number": "#D19A66",
    "prompt": "bold #7EB6FF",
}

CUSTOM_THEME = Theme(THEME_DICT) if RICH_AVAILABLE and Theme else None  # type: ignore[arg-type]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BRANDING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOGO_ART = """
[#7EB6FF]╭─────────────────────────────────────────────────────────────────╮[/]
[#7EB6FF]│[/]  [bold #E0B0FF]  ██████╗  ██████╗  ██████╗    ██████╗██╗  ██╗ █████╗ ████████╗[/]  [#7EB6FF]│[/]
[#7EB6FF]│[/]  [bold #E0B0FF]  ██╔══██╗██╔═══██╗██╔════╝   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝[/]  [#7EB6FF]│[/]
[#7EB6FF]│[/]  [bold #E0B0FF]  ██║  ██║██║   ██║██║        ██║     ███████║███████║   ██║   [/]  [#7EB6FF]│[/]
[#7EB6FF]│[/]  [bold #E0B0FF]  ██║  ██║██║   ██║██║        ██║     ██╔══██║██╔══██║   ██║   [/]  [#7EB6FF]│[/]
[#7EB6FF]│[/]  [bold #E0B0FF]  ██████╔╝╚██████╔╝╚██████╗   ╚██████╗██║  ██║██║  ██║   ██║   [/]  [#7EB6FF]│[/]
[#7EB6FF]│[/]  [bold #E0B0FF]  ╚═════╝  ╚═════╝  ╚═════╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   [/]  [#7EB6FF]│[/]
[#7EB6FF]╰─────────────────────────────────────────────────────────────────╯[/]
"""


class Icons:
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    ARROW = "→"
    BULLET = "•"
    DIAMOND = "◆"
    SEARCH = "🔍"
    BOOK = "📖"
    FILE = "📄"
    LINK = "🔗"
    GLOBE = "🌐"
    SPARKLE = "✨"
    DOT = "●"
    HELP = "?"
    EXIT = "⏻"
    CLEAR = "⌫"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA CLASSES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    messages: List[ChatMessage] = field(default_factory=list)
    loaded_docs: List[LoadedDocumentation] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, **metadata: Any) -> ChatMessage:
        msg = ChatMessage(role=role, content=content, metadata=metadata)
        self.messages.append(msg)
        return msg

    def clear(self) -> None:
        self.messages.clear()

    @property
    def doc_count(self) -> int:
        return len(self.loaded_docs)

    @property
    def total_pages(self) -> int:
        return sum(doc.page_count for doc in self.loaded_docs)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FALLBACK UTILITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class NullContext:
    def __init__(self, message: str = ""):
        self.message = message

    def __enter__(self) -> "NullContext":
        if self.message:
            print(f"[...] {self.message}")
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class NullProgress:
    def __enter__(self) -> "NullProgress":
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def add_task(self, *args: Any, **kwargs: Any) -> int:
        return 0

    def update(self, *args: Any, **kwargs: Any) -> None:
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class DocumentationCLI:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = ChatSession()
        self.console: Optional["RichConsole"] = None

        if RICH_AVAILABLE and Console is not None:
            self.console = Console(theme=CUSTOM_THEME)  # type: ignore[arg-type]

        self.scraper = WebScraper(config)
        self.site_identifier = SiteIdentifier(config)
        self.loader = DocumentationLoader(config, self.scraper, self.site_identifier)
        self.cache = CacheManager(config)
        self.processor = ContentProcessor(config)
        self.deep_search = DeepSearchOrchestrator(
            config, self.site_identifier, self.scraper
        )

        self.rag_engine = AgenticRAGEngine(
            config,
            identifier=self.site_identifier,
            scraper=self.scraper,
            processor=self.processor,
            cache=self.cache,
            deep_search=self.deep_search,
        )

        self.commands = {
            "/help": self.show_help,
            "/load": self.handle_load,
            "/url": self.handle_url,
            "/file": self.handle_file,
            "/find": self.handle_find,
            "/status": self.show_status,
            "/terms": self.handle_terms,
            "/term": self.handle_term,
            "/clear": self.handle_clear,
            "/exit": self.handle_exit,
        }

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OUTPUT HELPERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _print(self, *args: Any, **kwargs: Any) -> None:
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*[str(arg) for arg in args])

    def print_success(self, message: str) -> None:
        if self.console:
            self.console.print(f"[success]{Icons.SUCCESS}[/] {message}")
        else:
            print(f"[OK] {message}")

    def print_error(self, message: str) -> None:
        if self.console:
            self.console.print(f"[error]{Icons.ERROR}[/] [error]{message}[/]")
        else:
            print(f"[ERROR] {message}")

    def print_warning(self, message: str) -> None:
        if self.console:
            self.console.print(f"[warning]{Icons.WARNING}[/] [warning]{message}[/]")
        else:
            print(f"[WARN] {message}")

    def print_info(self, message: str) -> None:
        if self.console:
            self.console.print(f"[info]{Icons.INFO}[/] [info]{message}[/]")
        else:
            print(f"[INFO] {message}")

    def print_rule(self, title: str = "", style: str = "muted") -> None:
        if self.console and Rule is not None:
            self.console.print(Rule(title, style=style))  # type: ignore[misc]
        else:
            print(f"--- {title} ---" if title else "---")

    def create_spinner(self, message: str) -> Any:
        if self.console:
            return self.console.status(
                f"[#7EB6FF]{message}[/]",
                spinner="dots",
                spinner_style="#7EB6FF",
            )
        return NullContext(message)

    def create_progress(self) -> Any:
        if self.console and Progress is not None:
            return Progress(  # type: ignore[misc]
                SpinnerColumn(spinner_name="dots", style="#7EB6FF"),  # type: ignore[misc]
                TextColumn("[#7EB6FF]{task.description}[/]"),  # type: ignore[misc]
                BarColumn(complete_style="#7EB6FF", finished_style="success"),  # type: ignore[misc]
                TextColumn("[muted]{task.percentage:>3.0f}%[/]"),  # type: ignore[misc]
                console=self.console,
            )
        return NullProgress()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WELCOME & HELP SCREENS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def show_welcome(self) -> None:
        if not self.console:
            print("\n=== Documentation Chat CLI ===")
            print("Type /help for commands, or ask a question.\n")
            return

        self.console.clear()
        self.console.print(LOGO_ART)

        tagline = Align.center(  # type: ignore[union-attr]
            Text.from_markup(  # type: ignore[union-attr]
                "[italic #A0A0A0]Ask questions, get answers from any documentation[/]"
            )
        )
        self.console.print(tagline)
        self.console.print()

        quick_start = Table.grid(padding=(0, 2))  # type: ignore[union-attr]
        quick_start.add_column(style="command", justify="right")
        quick_start.add_column(style="muted")
        quick_start.add_row("/load React", "Load documentation by name")
        quick_start.add_row("/url https://...", "Load from URL")
        quick_start.add_row("/help", "Show all commands")

        quick_panel = Panel(  # type: ignore[misc]
            quick_start,
            title="[#7EB6FF]Quick Start[/]",
            title_align="left",
            border_style="#5C6370",
            box=ROUNDED,  # type: ignore[arg-type]
            padding=(1, 2),
        )
        self.console.print(Align.center(quick_panel, width=60))  # type: ignore[union-attr]
        self.console.print()

        tip = Text.from_markup(  # type: ignore[union-attr]
            f"[muted]{Icons.SPARKLE} Tip: Load documentation first, then ask questions naturally[/]"
        )
        self.console.print(Align.center(tip))  # type: ignore[union-attr]
        self.console.print()
        self.print_rule()

    def show_help(self) -> None:
        if not self.console:
            print("\nCommands:")
            print("  /load <name>   - Load docs by library name")
            print("  /url <url>     - Load docs from URL")
            print("  /file <path>   - Load docs from file")
            print("  /find <name>   - Find docs without loading")
            print("  /status        - Show loaded docs")
            print("  /terms <query> - Search terminology")
            print("  /term <name>   - Get term info")
            print("  /clear         - Clear history")
            print("  /exit          - Exit CLI\n")
            return

        self.console.print()

        cmd_table = Table(  # type: ignore[misc]
            show_header=True,
            header_style="bold #7EB6FF",
            box=ROUNDED,  # type: ignore[arg-type]
            border_style="#5C6370",
            padding=(0, 1),
            expand=False,
        )

        cmd_table.add_column("Command", style="command", no_wrap=True)
        cmd_table.add_column("Description")
        cmd_table.add_column("Example", style="#5C6370 italic")

        commands_data = [
            (f"{Icons.BOOK} /load <name>", "Load docs by library name", "/load React"),
            (
                f"{Icons.GLOBE} /url <url>",
                "Load docs from URL",
                "/url https://fastapi.tiangolo.com",
            ),
            (
                f"{Icons.FILE} /file <path>",
                "Load docs from local file",
                "/file ./docs/api.md",
            ),
            (
                f"{Icons.SEARCH} /find <name>",
                "Find docs without loading",
                "/find pandas",
            ),
            (f"{Icons.DOT} /status", "Show loaded documentation", "/status"),
            (
                f"{Icons.SEARCH} /terms <query>",
                "Search terminology",
                "/terms authentication",
            ),
            (f"{Icons.INFO} /term <name>", "Get term information", "/term useState"),
            (f"{Icons.CLEAR} /clear", "Clear conversation history", "/clear"),
            (f"{Icons.EXIT} /exit", "Exit the CLI", "/exit"),
        ]

        for cmd, desc, example in commands_data:
            cmd_table.add_row(cmd, desc, example)

        help_panel = Panel(  # type: ignore[misc]
            cmd_table,
            title=f"[title]{Icons.HELP} Commands[/]",
            title_align="left",
            border_style="#7EB6FF",
            box=ROUNDED,  # type: ignore[arg-type]
            padding=(1, 1),
        )

        self.console.print(help_panel)

        tips = Text()  # type: ignore[misc]
        tips.append(f"\n{Icons.SPARKLE} ", style="#FFB86C")
        tips.append("Tips:\n", style="bold")
        tips.append(f"  {Icons.BULLET} ", style="muted")
        tips.append("Load docs first, then ask questions naturally\n")
        tips.append(f"  {Icons.BULLET} ", style="muted")
        tips.append("Use /find to preview before loading\n")
        tips.append(f"  {Icons.BULLET} ", style="muted")
        tips.append("Multiple docs can be loaded simultaneously\n")

        self.console.print(tips)
        self.console.print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATUS DISPLAY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def show_status(self) -> None:
        if not self.console:
            print(
                f"\nLoaded: {self.session.doc_count} docs, {self.session.total_pages} pages"
            )
            print(f"Messages: {len(self.session.messages)}\n")
            return

        self.console.print()

        status_grid = Table.grid(padding=(0, 3))  # type: ignore[union-attr]
        status_grid.add_column(justify="center")
        status_grid.add_column(justify="center")
        status_grid.add_column(justify="center")

        def stat_box(value: str, label: str, color: str) -> Any:
            content = Text()  # type: ignore[misc]
            content.append(f"{value}\n", style=f"bold {color}")
            content.append(label, style="muted")
            return Panel(  # type: ignore[misc]
                Align.center(content),  # type: ignore[union-attr]
                box=ROUNDED,  # type: ignore[arg-type]
                border_style="#5C6370",
                width=20,
            )

        status_grid.add_row(
            stat_box(str(self.session.doc_count), "Sources", "#7EB6FF"),
            stat_box(str(self.session.total_pages), "Pages", "#98C379"),
            stat_box(str(len(self.session.messages)), "Messages", "#E0B0FF"),
        )

        self.console.print(Align.center(status_grid))  # type: ignore[union-attr]
        self.console.print()

        if self.session.loaded_docs:
            docs_table = Table(  # type: ignore[misc]
                show_header=True,
                header_style="bold #7EB6FF",
                box=ROUNDED,  # type: ignore[arg-type]
                border_style="#5C6370",
                expand=True,
            )

            docs_table.add_column("#", style="number", width=4)
            docs_table.add_column("Source")
            docs_table.add_column("Method", style="muted")
            docs_table.add_column("Pages", style="number", justify="right")
            docs_table.add_column("Size", style="muted", justify="right")

            for i, doc in enumerate(self.session.loaded_docs, 1):
                method_icon = {
                    LoadMethod.NAME_SEARCH: Icons.SEARCH,
                    LoadMethod.URL: Icons.GLOBE,
                    LoadMethod.FILE_UPLOAD: Icons.FILE,
                }.get(doc.method, Icons.DOT)

                size_kb = doc.total_content_length / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb > 0 else "0 KB"

                docs_table.add_row(
                    str(i),
                    doc.source,
                    f"{method_icon} {doc.method.name.replace('_', ' ').title()}",
                    str(doc.page_count),
                    size_str,
                )

            docs_panel = Panel(  # type: ignore[misc]
                docs_table,
                title=f"[title]{Icons.BOOK} Loaded Documentation[/]",
                title_align="left",
                border_style="#7EB6FF",
            )
            self.console.print(docs_panel)
        else:
            empty_msg = Panel(  # type: ignore[misc]
                Align.center(  # type: ignore[union-attr]
                    Text.from_markup(  # type: ignore[union-attr]
                        f"[muted]{Icons.INFO} No documentation loaded yet\n"
                        f"Use [command]/load[/] [muted]<name>[/] or [command]/url[/] [muted]<url>[/] to get started[/]"
                    )
                ),
                border_style="#5C6370",
                padding=(1, 2),
            )
            self.console.print(empty_msg)

        self.console.print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COMMAND HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_load(self, name: str) -> None:
        if not name:
            self.print_error("Usage: /load <library name>")
            return

        with self.create_spinner(f"Searching for '{name}' documentation..."):
            try:
                result = await self.loader.load_by_name(name)
                self.session.loaded_docs.append(result)

                if self.config.terminology.enabled:
                    for page in result.pages:
                        await self.rag_engine.extract_and_index_terminology(page)

            except Exception as exc:
                self.print_error(f"Failed to load '{name}': {exc}")
                return

        self.print_success(f"Loaded {result.page_count} pages from '{name}'")

        if result.metadata.get("candidate_urls"):
            urls = result.metadata["candidate_urls"][:3]
            self.print_info(f"Source: {urls[0]}")

        if self.config.terminology.enabled:
            term_count = result.metadata.get("terms_extracted", 0)
            if term_count > 0:
                self.print_info(f"Extracted {term_count} terms")

    async def handle_url(self, url: str) -> None:
        if not url:
            self.print_error("Usage: /url <url>")
            return

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        with self.create_spinner(f"Loading documentation from {url}..."):
            try:
                result = await self.loader.load_from_url(url, follow_links=True)
                self.session.loaded_docs.append(result)

                if self.config.terminology.enabled:
                    for page in result.pages:
                        await self.rag_engine.extract_and_index_terminology(page)

            except Exception as exc:
                self.print_error(f"Failed to load URL: {exc}")
                return

        self.print_success(f"Loaded {result.page_count} pages from URL")

        if result.pages:
            self.print_info(f"Title: {result.pages[0].title}")

    async def handle_file(self, path: str) -> None:
        if not path:
            self.print_error("Usage: /file <path>")
            return

        file_path = Path(path).expanduser().resolve()

        if not file_path.exists():
            self.print_error(f"File not found: {file_path}")
            return

        with self.create_spinner(f"Loading {file_path.name}..."):
            try:
                content = file_path.read_text(encoding="utf-8")
                result = await self.loader.load_from_file(content, file_path.name)
                self.session.loaded_docs.append(result)

                if self.config.terminology.enabled and result.pages:
                    await self.rag_engine.extract_and_index_terminology(result.pages[0])

            except Exception as exc:
                self.print_error(f"Failed to load file: {exc}")
                return

        self.print_success(f"Loaded file: {file_path.name}")

    async def handle_find(self, name: str) -> None:
        if not name:
            self.print_error("Usage: /find <name>")
            return

        with self.create_spinner(f"Searching for '{name}'..."):
            try:
                candidates = await self.loader.finder.find_documentation(name)
            except Exception as exc:
                self.print_error(f"Search failed: {exc}")
                return

        if not candidates:
            self.print_warning(f"No documentation found for '{name}'")
            return

        if self.console:
            results_table = Table(  # type: ignore[misc]
                show_header=True,
                header_style="bold #7EB6FF",
                box=ROUNDED,  # type: ignore[arg-type]
                border_style="#5C6370",
                expand=True,
            )

            results_table.add_column("#", style="number", width=4)
            results_table.add_column("Title")
            results_table.add_column("URL", style="url")
            results_table.add_column("Score", style="number", justify="right")

            for i, candidate in enumerate(candidates, 1):
                url_display = (
                    candidate.url[:47] + "..."
                    if len(candidate.url) > 50
                    else candidate.url
                )
                title_display = (
                    candidate.title[:37] + "..."
                    if len(candidate.title) > 40
                    else candidate.title
                )

                results_table.add_row(
                    str(i), title_display, url_display, f"{candidate.confidence:.2f}"
                )

            results_panel = Panel(  # type: ignore[misc]
                results_table,
                title=f"[title]{Icons.SEARCH} Documentation for '{name}'[/]",
                title_align="left",
                border_style="#7EB6FF",
            )
            self.console.print()
            self.console.print(results_panel)
            self.console.print()
            self.print_info("Use /url <url> to load a specific documentation site")
        else:
            print(f"\nDocumentation for '{name}':")
            for i, c in enumerate(candidates, 1):
                print(f"  {i}. {c.title} - {c.url} ({c.confidence:.2f})")
            print()

    async def handle_terms(self, query: str) -> None:
        if not query:
            self.print_error("Usage: /terms <query>")
            return

        if not self.config.terminology.enabled:
            self.print_warning("Terminology system is disabled")
            return

        with self.create_spinner("Searching terminology..."):
            try:
                results = await self.rag_engine._terminology_indexer.search_terms(
                    query, limit=10
                )
            except Exception as exc:
                self.print_error(f"Search failed: {exc}")
                return

        if not results:
            self.print_warning(f"No terms found for '{query}'")
            return

        if self.console:
            terms = []
            for r in results[:8]:
                term_name = (
                    r.get("file", "")
                    .split("/")[-1]
                    .replace("term_", "")
                    .replace(".md", "")
                )
                terms.append(term_name)

            term_text = ", ".join(terms)
            term_panel = Panel(  # type: ignore[misc]
                term_text,
                title=f"[title]{Icons.SEARCH} Relevant Terms[/]",
                title_align="left",
                border_style="#7EB6FF",
            )
            self.console.print()
            self.console.print(term_panel)
            self.console.print()
        else:
            print("\nRelevant terms:")
            for r in results[:8]:
                print(f"  - {r.get('file', 'unknown')}")

    async def handle_term(self, term: str) -> None:
        if not term:
            self.print_error("Usage: /term <term name>")
            return

        if not self.config.terminology.enabled:
            self.print_warning("Terminology system is disabled")
            return

        with self.create_spinner(f"Looking up '{term}'..."):
            try:
                hierarchy = await self.rag_engine.get_term_hierarchy(term)
            except Exception as exc:
                self.print_error(f"Lookup failed: {exc}")
                return

        if not hierarchy:
            self.print_warning(f"Term '{term}' not found")
            return

        if self.console:
            info_table = Table.grid(padding=(0, 2))  # type: ignore[union-attr]
            info_table.add_column(style="muted")
            info_table.add_column()

            if hierarchy.get("parents"):
                info_table.add_row("Parents:", ", ".join(hierarchy["parents"]))
            if hierarchy.get("related"):
                info_table.add_row("Related:", ", ".join(hierarchy["related"][:5]))
            if hierarchy.get("connections"):
                info_table.add_row("Connections:", str(hierarchy["connections"]))

            term_panel = Panel(  # type: ignore[misc]
                info_table,
                title=f"[title]{Icons.INFO} Term: {term}[/]",
                title_align="left",
                border_style="#7EB6FF",
            )
            self.console.print()
            self.console.print(term_panel)
            self.console.print()
        else:
            print(f"\nTerm: {term}")
            for k, v in hierarchy.items():
                print(f"  {k}: {v}")

    async def handle_clear(self) -> None:
        self.session.clear()
        self.print_success("Conversation history cleared")

    async def handle_exit(self) -> None:
        self.print_info("Goodbye!")
        raise SystemExit(0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # QUESTION HANDLING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def handle_question(self, question: str) -> None:
        if not self.session.loaded_docs:
            self.print_warning("No documentation loaded. Use /load or /url first.")
            return

        self.session.add_message("user", question)

        with self.create_spinner("Thinking..."):
            try:
                result = await self.rag_engine.terminology_aware_search(question)
            except Exception as exc:
                self.print_error(f"Failed to process question: {exc}")
                return

        answer = result.get("answer", "I couldn't find an answer.")
        self.session.add_message("assistant", answer)

        if self.console:
            selected_terms = result.get("terminology", {}).get("selected_terms", [])
            if selected_terms:
                terms_text = Text()  # type: ignore[misc]
                terms_text.append(f"{Icons.SPARKLE} Related Terms: ", style="muted")
                terms_text.append(", ".join(selected_terms[:5]), style="#7EB6FF")
                self.console.print()
                self.console.print(terms_text)

            self.console.print()
            answer_panel = Panel(  # type: ignore[misc]
                Markdown(answer),  # type: ignore[misc]
                title="[title]Answer[/]",
                title_align="left",
                border_style="#7EB6FF",
                padding=(1, 2),
            )
            self.console.print(answer_panel)

            sources = result.get("top_chunks", [])[:3]
            if sources:
                sources_text = Text()  # type: ignore[misc]
                sources_text.append(f"\n{Icons.LINK} Sources: ", style="muted")
                urls = [
                    s.get("site", {}).get("url", "")
                    for s in sources
                    if s.get("site", {}).get("url")
                ]
                sources_text.append(", ".join(set(urls)), style="url")
                self.console.print(sources_text)

            self.console.print()
        else:
            print(f"\n{answer}\n")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MAIN LOOP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_prompt(self) -> str:
        doc_indicator = (
            f"[{self.session.doc_count} docs]" if self.session.doc_count > 0 else ""
        )

        if self.console:
            prompt_parts = []
            if doc_indicator:
                prompt_parts.append(f"[number]{doc_indicator}[/]")
            prompt_parts.append("[prompt]>[/]")
            return " ".join(prompt_parts) + " "
        return f"{doc_indicator} > "

    async def process_input(self, user_input: str) -> None:
        user_input = user_input.strip()

        if not user_input:
            return

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command in self.commands:
                handler = self.commands[command]
                if asyncio.iscoroutinefunction(handler):
                    if command in ("/help", "/status", "/clear", "/exit"):
                        await handler()
                    else:
                        await handler(args)
                else:
                    handler()
            else:
                self.print_error(f"Unknown command: {command}")
                self.print_info("Type /help for available commands")
        else:
            await self.handle_question(user_input)

    async def run(self) -> None:
        self.show_welcome()

        try:
            while True:
                try:
                    if self.console:
                        prompt = self.get_prompt()
                        self.console.print(prompt, end="")
                        user_input = input()
                    else:
                        user_input = input(self.get_prompt())

                    await self.process_input(user_input)

                except KeyboardInterrupt:
                    if self.console:
                        self.console.print()
                    else:
                        print()
                    self.print_info("Use /exit to quit")
                    continue
                except EOFError:
                    break

        finally:
            await self.scraper.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def run_cli(config_path: Optional[str] = None) -> None:
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        if RICH_AVAILABLE and Console is not None:
            console = Console(theme=CUSTOM_THEME)  # type: ignore[arg-type]
            console.print(f"[error]{Icons.ERROR} Configuration error: {exc}[/]")
        else:
            print(f"Configuration error: {exc}")
        sys.exit(1)
    except Exception as exc:
        if RICH_AVAILABLE and Console is not None:
            console = Console(theme=CUSTOM_THEME)  # type: ignore[arg-type]
            console.print(f"[error]{Icons.ERROR} Failed to start: {exc}[/]")
        else:
            print(f"Failed to start: {exc}")
        sys.exit(1)

    cli = DocumentationCLI(config)
    asyncio.run(cli.run())


if __name__ == "__main__":
    run_cli()
