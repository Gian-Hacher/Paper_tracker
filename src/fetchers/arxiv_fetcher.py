from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import feedparser
import requests

from src.models.paper import Paper

logger = logging.getLogger(__name__)


class ArxivFetcher:
    def __init__(
        self,
        endpoint: str,
        categories: list[str],
        max_results: int = 200,
        timeout_seconds: int = 20,
    ) -> None:
        self.endpoint = endpoint
        self.categories = categories
        self.max_results = max_results
        self.timeout_seconds = timeout_seconds

    def _build_query_url(self) -> str:
        category_query = " OR ".join(f"cat:{cat}" for cat in self.categories)
        params = {
            "search_query": category_query,
            "start": 0,
            "max_results": self.max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        return f"{self.endpoint}?{urlencode(params)}"

    def _parse_entry(self, entry: Any) -> Paper:
        categories = [tag["term"] for tag in getattr(entry, "tags", []) if "term" in tag]
        authors = [author.name for author in getattr(entry, "authors", [])]
        paper_id = entry.id.split("/")[-1]

        return Paper(
            paper_id=paper_id,
            title=getattr(entry, "title", "").strip(),
            abstract=getattr(entry, "summary", "").strip(),
            authors=authors,
            published_date=getattr(entry, "published", ""),
            updated_date=getattr(entry, "updated", ""),
            source="arxiv",
            primary_category=getattr(entry, "arxiv_primary_category", {}).get("term", ""),
            categories=categories,
            arxiv_url=getattr(entry, "link", ""),
            pdf_url=f"https://arxiv.org/pdf/{paper_id}.pdf",
            venue_raw=getattr(entry, "arxiv_journal_ref", "") or "",
        )

    @staticmethod
    def _is_recent(paper: Paper, days_back: int) -> bool:
        try:
            published = datetime.fromisoformat(paper.published_date.replace("Z", "+00:00"))
        except ValueError:
            return False
        threshold = datetime.now(timezone.utc) - timedelta(days=days_back)
        return published >= threshold

    def fetch(self, days_back: int = 7) -> list[Paper]:
        url = self._build_query_url()
        logger.info("Fetching arXiv feed: %s", url)

        try:
            response = requests.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("arXiv request failed: %s", exc)
            return []

        parsed = feedparser.parse(response.text)
        if getattr(parsed, "bozo", False):
            logger.warning("arXiv feed parser reported bozo=%s", parsed.bozo)

        papers: list[Paper] = []
        for entry in parsed.entries:
            paper = self._parse_entry(entry)
            if self._is_recent(paper, days_back):
                papers.append(paper)

        logger.info("Fetched %d recent papers from arXiv", len(papers))
        return papers
