from src.models.paper import Paper
from src.processors.select import select_top_papers


def _paper(index: int, title: str, abstract: str) -> Paper:
    day = (index % 9) + 1
    return Paper(
        paper_id=f"paper-{index}",
        title=title,
        abstract=abstract,
        authors=["A"],
        published_date=f"2026-03-0{day}T00:00:00+00:00",
        updated_date=f"2026-03-0{day}T00:00:00+00:00",
        source="openalex",
        primary_category="robotics",
        categories=["robotics"],
        arxiv_url="https://example.org",
        pdf_url="https://example.org/pdf",
        venue_raw="Science Robotics",
        venue_name="Science Robotics",
        venue_tier="first",
        venue_type="journal",
    )


def test_select_top_papers_backfills_when_strict_results_are_insufficient() -> None:
    strict_match = _paper(1, "Robot manipulation policy", "Imitation learning for manipulation.")
    relaxed_pool = [
        _paper(i, f"General robotics paper {i}", "Robotics systems and experiments.")
        for i in range(2, 8)
    ]
    cfg = {
        "recency": {"window_days": 30, "max_score": 40.0},
        "keyword": {"max_hits": 5, "max_score": 40.0},
        "source": {"default_score": 10.0, "source_scores": {"openalex": 20.0}},
        "weights": {"recency_weight": 1.0, "keyword_weight": 1.0, "source_weight": 1.0},
    }

    strict_filtered, relaxed_filtered, selected = select_top_papers(
        papers=[strict_match, *relaxed_pool],
        include_keywords=["robot manipulation", "imitation learning"],
        exclude_keywords=["autonomous driving"],
        scoring_config=cfg,
        top_n=5,
    )

    assert len(strict_filtered) == 1
    assert len(relaxed_filtered) == 7
    assert len(selected) == 5
    assert selected[0].paper_id == "paper-1"
