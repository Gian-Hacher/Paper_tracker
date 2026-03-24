from datetime import datetime, timedelta, timezone

from src.models.paper import Paper
from src.processors.score import score_paper


def _paper_with_date(days_ago: int) -> Paper:
    published = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return Paper(
        paper_id="score-1",
        title="Diffusion Policy for Robot Manipulation",
        abstract="Embodied robot learning.",
        authors=["A"],
        published_date=published.isoformat(),
        updated_date=published.isoformat(),
        source="arxiv",
        primary_category="cs.RO",
        categories=["cs.RO"],
        arxiv_url="https://arxiv.org/abs/0000.0001",
        pdf_url="https://arxiv.org/pdf/0000.0001.pdf",
        keywords_matched=["diffusion policy", "robot learning"],
    )


def test_score_assigns_higher_recency_to_new_paper() -> None:
    cfg = {
        "recency": {"window_days": 30, "max_score": 40.0},
        "keyword": {"max_hits": 5, "max_score": 40.0},
        "source": {"default_score": 10.0, "source_scores": {"arxiv": 20.0}},
        "weights": {"recency_weight": 1.0, "keyword_weight": 1.0, "source_weight": 1.0},
    }
    fresh = score_paper(_paper_with_date(1), cfg)
    old = score_paper(_paper_with_date(25), cfg)
    assert fresh.recency_score > old.recency_score
    assert fresh.total_score > old.total_score

