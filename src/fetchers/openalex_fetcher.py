from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import requests

from src.models.paper import Paper
from src.utils.venue_utils import VenueEntry, VenueMatcher

logger = logging.getLogger(__name__)


def _rebuild_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return ""
    positions: list[tuple[int, str]] = []
    for token, idx_list in inverted_index.items():
        for idx in idx_list:
            positions.append((idx, token))
    if not positions:
        return ""
    positions.sort(key=lambda x: x[0])
    return " ".join(token for _, token in positions)


def _extract_openalex_id(raw_id: str) -> str:
    return (raw_id or "").rstrip("/").split("/")[-1]


class OpenAlexFetcher:
    def __init__(
        self,
        works_endpoint: str,
        sources_endpoint: str,
        works_per_page: int = 100,
        source_lookup_per_page: int = 8,
        timeout_seconds: int = 30,
        mailto: str = "",
    ) -> None:
        self.works_endpoint = works_endpoint
        self.sources_endpoint = sources_endpoint
        self.works_per_page = max(1, min(int(works_per_page), 200))
        self.source_lookup_per_page = max(1, min(int(source_lookup_per_page), 200))
        self.timeout_seconds = timeout_seconds
        self.mailto = mailto

    def resolve_source_ids(
        self,
        venue_entries: list[VenueEntry],
        venue_matcher: VenueMatcher,
    ) -> dict[str, str]:
        resolved: dict[str, str] = {}
        for entry in venue_entries:
            source_id = self._resolve_single_source_id(entry, venue_matcher)
            if source_id:
                resolved[entry.canonical_name] = source_id
            else:
                logger.warning("Could not resolve OpenAlex source id for venue: %s", entry.canonical_name)
        logger.info("Resolved %d/%d venue source ids from OpenAlex", len(resolved), len(venue_entries))
        return resolved

    def _resolve_single_source_id(
        self,
        venue_entry: VenueEntry,
        venue_matcher: VenueMatcher,
    ) -> str | None:
        for query in [venue_entry.canonical_name, *venue_entry.aliases]:
            params = {
                "search": query,
                "per-page": self.source_lookup_per_page,
            }
            if self.mailto:
                params["mailto"] = self.mailto

            try:
                response = requests.get(self.sources_endpoint, params=params, timeout=self.timeout_seconds)
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as exc:
                logger.warning("OpenAlex source lookup failed for '%s': %s", query, exc)
                continue

            for source in payload.get("results", []):
                candidate_names = self._source_candidate_names(source)
                for candidate_name in candidate_names:
                    matched = venue_matcher.match(candidate_name)
                    if matched and matched.canonical_name == venue_entry.canonical_name:
                        return _extract_openalex_id(source.get("id", ""))
        return None

    @staticmethod
    def _source_candidate_names(source: dict) -> list[str]:
        names: list[str] = []
        for key in ("display_name", "abbreviated_title"):
            value = source.get(key)
            if value:
                names.append(value)
        alternate_titles = source.get("alternate_titles") or []
        names.extend([title for title in alternate_titles if title])
        return names

    def fetch_all_by_sources(
        self,
        days_back: int,
        source_ids: list[str],
    ) -> list[Paper]:
        if not source_ids:
            logger.info("Skipping OpenAlex work fetch because source ids are empty")
            return []

        from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).date().isoformat()
        source_filter = "|".join(sorted(set(source_ids)))
        papers: list[Paper] = []
        cursor = "*"

        logger.info(
            "Fetching all OpenAlex works from %s across %d sources",
            from_date,
            len(set(source_ids)),
        )
        while cursor:
            params = {
                "filter": (
                    f"from_publication_date:{from_date},"
                    f"primary_location.source.id:{source_filter}"
                ),
                "sort": "publication_date:desc",
                "per-page": self.works_per_page,
                "cursor": cursor,
            }
            if self.mailto:
                params["mailto"] = self.mailto

            try:
                response = requests.get(self.works_endpoint, params=params, timeout=self.timeout_seconds)
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as exc:
                logger.warning("OpenAlex work fetch failed for cursor '%s': %s", cursor, exc)
                break

            for work in payload.get("results", []):
                paper = self._parse_work(work)
                papers.append(paper)

            cursor = (payload.get("meta") or {}).get("next_cursor")
            if not payload.get("results"):
                break

        logger.info("Fetched %d papers from OpenAlex source-constrained crawl", len(papers))
        return papers

    def _parse_work(self, work: dict) -> Paper:
        work_id = _extract_openalex_id(work.get("id") or "")
        authors = [
            auth.get("author", {}).get("display_name", "")
            for auth in work.get("authorships", [])
            if auth.get("author", {}).get("display_name")
        ]

        primary_location = work.get("primary_location", {}) or {}
        source_obj = primary_location.get("source", {}) or {}
        landing_page = primary_location.get("landing_page_url") or work.get("doi") or work.get("id") or ""
        pdf_url = primary_location.get("pdf_url") or ""

        publication_date = work.get("publication_date") or ""
        if publication_date and "T" not in publication_date:
            publication_date = f"{publication_date}T00:00:00+00:00"

        updated_date = work.get("updated_date") or publication_date
        if updated_date and "T" not in updated_date:
            updated_date = f"{updated_date}T00:00:00+00:00"

        categories = [c.get("display_name", "") for c in work.get("concepts", []) if c.get("display_name")]
        primary_topic = ((work.get("primary_topic") or {}).get("field") or {}).get("display_name", "")

        return Paper(
            paper_id=work_id or work.get("doi", ""),
            title=work.get("title", "") or "",
            abstract=_rebuild_abstract(work.get("abstract_inverted_index")),
            authors=authors,
            published_date=publication_date,
            updated_date=updated_date,
            source="openalex",
            primary_category=primary_topic,
            categories=categories,
            arxiv_url=landing_page,
            pdf_url=pdf_url,
            venue_raw=source_obj.get("display_name", "") or "",
        )
