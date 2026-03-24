from __future__ import annotations

from src.models.paper import Paper
from src.utils.text_utils import normalize_text


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Deduplicate by paper_id first, then by normalized title."""
    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    deduped: list[Paper] = []

    for paper in papers:
        if paper.paper_id in seen_ids:
            continue

        normalized_title = normalize_text(paper.title)
        if normalized_title in seen_titles:
            continue

        seen_ids.add(paper.paper_id)
        seen_titles.add(normalized_title)
        deduped.append(paper)
    return deduped

