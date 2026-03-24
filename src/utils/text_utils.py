from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace for stable matching."""
    cleaned = re.sub(r"\s+", " ", text or "").strip().lower()
    return cleaned


def build_search_text(title: str, abstract: str) -> str:
    return normalize_text(f"{title} {abstract}")
