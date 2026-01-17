"""Simple TTL-based cache for fetched documentation."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, Optional

from .settings import Config


@dataclass
class CacheEntry:
    value: Any
    timestamp: float


class CacheManager:
    """Thread-safe TTL cache to avoid redundant scrapes."""

    def __init__(self, config: Config) -> None:
        self._ttl = config.cache.ttl
        self._max_size = config.cache.max_size
        self._store: Dict[str, CacheEntry] = {}
        self._lock = RLock()

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [key for key, entry in self._store.items() if now - entry.timestamp > self._ttl]
        for key in expired:
            self._store.pop(key, None)

    def _evict_overflow(self) -> None:
        if len(self._store) <= self._max_size:
            return
        # Remove the oldest entries first
        sorted_items = sorted(self._store.items(), key=lambda item: item[1].timestamp)
        overflow = len(self._store) - self._max_size
        for key, _ in sorted_items[:overflow]:
            self._store.pop(key, None)

    @staticmethod
    def make_key(*parts: Any) -> str:
        serialized = json.dumps(parts, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._evict_expired()
            entry = self._store.get(key)
            if entry is None:
                return None
            return entry.value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = CacheEntry(value=value, timestamp=time.time())
            self._evict_expired()
            self._evict_overflow()
