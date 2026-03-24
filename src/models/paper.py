from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Paper:
    """Unified paper model used across fetching, processing, and storage."""

    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    published_date: str
    updated_date: str
    source: str
    primary_category: str
    categories: list[str]
    arxiv_url: str
    pdf_url: str
    venue_raw: str = ""
    venue_name: str = ""
    venue_tier: str = ""
    venue_type: str = ""
    keywords_matched: list[str] = field(default_factory=list)
    recency_score: float = 0.0
    keyword_score: float = 0.0
    source_score: float = 0.0
    total_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "published_date": self.published_date,
            "updated_date": self.updated_date,
            "source": self.source,
            "primary_category": self.primary_category,
            "categories": self.categories,
            "arxiv_url": self.arxiv_url,
            "pdf_url": self.pdf_url,
            "venue_raw": self.venue_raw,
            "venue_name": self.venue_name,
            "venue_tier": self.venue_tier,
            "venue_type": self.venue_type,
            "keywords_matched": self.keywords_matched,
            "recency_score": self.recency_score,
            "keyword_score": self.keyword_score,
            "source_score": self.source_score,
            "total_score": self.total_score,
        }
