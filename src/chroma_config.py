from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure .env (if present) is loaded before we read env vars.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]


def _resolve_path(value: Optional[str], default_relative: str) -> str:
    """Resolve a path relative to the project root unless it is already absolute."""
    raw = value or default_relative
    path = Path(raw)
    if not path.is_absolute():
        path = BASE_DIR / path
    return str(path)


@dataclass(frozen=True)
class ChromaConfig:
    path: str
    collection: str
    chunked_json: str


@lru_cache(maxsize=1)
def get_chroma_config() -> ChromaConfig:
    """Return the shared Chroma configuration sourced from env vars/.env."""
    return ChromaConfig(
        path=_resolve_path(os.environ.get("CHROMA_PATH"), "voxeurop_db"),
        collection=os.environ.get("CHROMA_COLLECTION", "voxeurop_articles"),
        chunked_json=_resolve_path(
            os.environ.get("CHUNKED_JSON"),
            "data/chunked/chunked_articles.json",
        ),
    )
