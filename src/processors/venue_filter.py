from __future__ import annotations

from src.models.paper import Paper
from src.utils.venue_utils import VenueMatcher


def filter_and_annotate_by_venue(
    papers: list[Paper],
    matcher: VenueMatcher,
) -> list[Paper]:
    """Keep only papers matched to whitelist venues and annotate canonical venue info."""
    filtered: list[Paper] = []
    for paper in papers:
        matched = matcher.match(paper.venue_raw)
        if matched is None:
            continue

        paper.venue_name = matched.canonical_name
        paper.venue_tier = matched.tier
        paper.venue_type = matched.venue_type
        filtered.append(paper)
    return filtered

