from __future__ import annotations

from src.models.paper import Paper
from src.utils.text_utils import build_search_text, normalize_text


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    normalized = normalize_text(text)
    hits: list[str] = []
    for keyword in keywords:
        keyword_n = normalize_text(keyword)
        if keyword_n and keyword_n in normalized:
            hits.append(keyword)
    return hits


def should_exclude(text: str, exclude_keywords: list[str]) -> bool:
    normalized = normalize_text(text)
    for keyword in exclude_keywords:
        keyword_n = normalize_text(keyword)
        if keyword_n and keyword_n in normalized:
            return True
    return False


def filter_papers(
    papers: list[Paper],
    include_keywords: list[str],
    exclude_keywords: list[str],
    require_include_match: bool = True,
) -> list[Paper]:
    filtered: list[Paper] = []
    for paper in papers:
        search_text = build_search_text(paper.title, paper.abstract)
        if should_exclude(search_text, exclude_keywords):
            continue

        hits = match_keywords(search_text, include_keywords)
        if require_include_match and not hits:
            continue

        paper.keywords_matched = hits
        filtered.append(paper)
    return filtered
