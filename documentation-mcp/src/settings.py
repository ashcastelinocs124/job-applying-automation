"""Configuration loading utilities for the Documentation MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

DEFAULT_CONFIG_PATH = Path("config/config.yaml")
ENV_CONFIG_PATH = "DOCUMENTATION_MCP_CONFIG"


@dataclass
class ServerSettings:
    name: str
    version: str
    host: str
    port: int


@dataclass
class ScrapingSettings:
    max_concurrent_requests: int
    request_delay: float
    timeout: int
    user_agent: str


@dataclass
class CacheSettings:
    ttl: int
    max_size: int
    storage_path: str


@dataclass
class RAGSettings:
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    max_context_length: int


@dataclass
class AISettings:
    model: str
    temperature: float
    max_tokens: int


@dataclass
class SiteSettings:
    patterns: List[str] = field(default_factory=list)
    excluded_domains: List[str] = field(default_factory=list)


@dataclass
class ZoektSettings:
    enabled: bool = True
    server_url: str = "http://localhost:6070"
    index_dir: str = "./zoekt-index"
    timeout: int = 30
    max_results: int = 100
    context_lines: int = 2


@dataclass
class ProactiveSettings:
    enabled: bool = True
    max_concurrent_indexing: int = 3
    index_queue_size: int = 100
    reindex_interval: int = 3600
    auto_index_on_scrape: bool = True


@dataclass
class PointListSettings:
    enabled: bool = True
    max_points_per_doc: int = 50
    extract_functions: bool = True
    extract_concepts: bool = True
    extract_examples: bool = True
    build_relationships: bool = True


@dataclass
class TerminologySettings:
    enabled: bool = True
    max_terms_per_page: int = 30
    index_dir: str = "./terminology-index"
    use_ai_extraction: bool = True
    use_ai_selection: bool = True
    confidence_threshold: float = 0.6
    build_knowledge_graph: bool = True
    auto_extract_on_scrape: bool = True


@dataclass
class Config:
    server: ServerSettings
    scraping: ScrapingSettings
    cache: CacheSettings
    rag: RAGSettings
    ai: AISettings
    sites: SiteSettings
    zoekt: ZoektSettings = field(default_factory=ZoektSettings)
    proactive: ProactiveSettings = field(default_factory=ProactiveSettings)
    point_list: PointListSettings = field(default_factory=PointListSettings)
    terminology: TerminologySettings = field(default_factory=TerminologySettings)
    raw: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return self.raw


class ConfigError(RuntimeError):
    """Raised when configuration loading fails."""


def _read_config_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse YAML config: {exc}") from exc


def _resolve_config_path(explicit_path: Optional[str] = None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve()

    env_path = os.getenv(ENV_CONFIG_PATH)
    if env_path:
        return Path(env_path).expanduser().resolve()

    return (Path.cwd() / DEFAULT_CONFIG_PATH).resolve()


def _build_config_objects(raw: Dict[str, Any]) -> Config:
    try:
        server_cfg = raw.get("server", {})
        scraping_cfg = raw.get("scraping", {})
        cache_cfg = raw.get("cache", {})
        rag_cfg = raw.get("rag", {})
        ai_cfg = raw.get("ai", {})
        site_cfg = raw.get("sites", {})
        zoekt_cfg = raw.get("zoekt", {})
        proactive_cfg = raw.get("proactive", {})
        point_list_cfg = raw.get("point_list", {})
        terminology_cfg = raw.get("terminology", {})

        config = Config(
            server=ServerSettings(**server_cfg),
            scraping=ScrapingSettings(**scraping_cfg),
            cache=CacheSettings(**cache_cfg),
            rag=RAGSettings(**rag_cfg),
            ai=AISettings(**ai_cfg),
            sites=SiteSettings(**site_cfg),
            zoekt=ZoektSettings(**zoekt_cfg) if zoekt_cfg else ZoektSettings(),
            proactive=ProactiveSettings(**proactive_cfg)
            if proactive_cfg
            else ProactiveSettings(),
            point_list=PointListSettings(**point_list_cfg)
            if point_list_cfg
            else PointListSettings(),
            terminology=TerminologySettings(**terminology_cfg)
            if terminology_cfg
            else TerminologySettings(),
            raw=raw,
        )
    except TypeError as exc:
        raise ConfigError(f"Invalid configuration structure: {exc}") from exc

    return config


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from YAML into strongly typed dataclasses."""

    config_path = _resolve_config_path(path)
    raw_config = _read_config_file(config_path)
    return _build_config_objects(raw_config)
