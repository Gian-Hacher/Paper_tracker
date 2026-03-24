from __future__ import annotations

from src.models.paper import Paper
from src.utils.text_utils import normalize_text


def normalize_paper(paper: Paper) -> Paper:
    """Apply lightweight normalization to text fields."""
    paper.title = " ".join((paper.title or "").split())
    paper.abstract = " ".join((paper.abstract or "").split())
    paper.primary_category = normalize_text(paper.primary_category)
    paper.categories = [normalize_text(category) for category in paper.categories]
    return paper

