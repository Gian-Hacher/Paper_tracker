from __future__ import annotations

from src.models.paper import Paper
from src.processors.filter import filter_papers
from src.processors.score import score_papers


def _sort_papers(papers: list[Paper]) -> list[Paper]:
    return sorted(
        papers,
        key=lambda paper: (paper.total_score, paper.published_date),
        reverse=True,
    )


def select_top_papers(
    papers: list[Paper],
    include_keywords: list[str],
    exclude_keywords: list[str],
    scoring_config: dict,
    top_n: int,
) -> tuple[list[Paper], list[Paper], list[Paper]]:
    """Select top papers in two stages.

    1. Strict stage: require include-keyword matches.
    2. Relaxed stage: if strict stage has too few papers, backfill with
       source-constrained papers that pass exclude-keyword filtering.
    """

    strict_filtered = filter_papers(
        papers=papers,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords,
        require_include_match=True,
    )
    strict_scored = _sort_papers(score_papers(strict_filtered, scoring_config))
    if len(strict_scored) >= top_n:
        return strict_filtered, strict_filtered, strict_scored[:top_n]

    relaxed_filtered = filter_papers(
        papers=papers,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords,
        require_include_match=False,
    )
    relaxed_scored = _sort_papers(score_papers(relaxed_filtered, scoring_config))

    selected: list[Paper] = []
    seen_ids: set[str] = set()
    for paper in strict_scored + relaxed_scored:
        if paper.paper_id in seen_ids:
            continue
        seen_ids.add(paper.paper_id)
        selected.append(paper)
        if len(selected) >= top_n:
            break

    return strict_filtered, relaxed_filtered, selected
