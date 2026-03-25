from src.models.paper import Paper
from src.renderers.markdown_report import (
    render_candidate_titles_markdown,
    render_release_summary_markdown,
)


def test_release_summary_contains_only_brief_fields() -> None:
    paper = Paper(
        paper_id="p1",
        title="A Robotics Paper",
        abstract="Detailed abstract.",
        authors=["Alice", "Bob"],
        published_date="2026-03-24T00:00:00+00:00",
        updated_date="2026-03-24T00:00:00+00:00",
        source="openalex",
        primary_category="robotics",
        categories=["robotics"],
        arxiv_url="https://example.org",
        pdf_url="https://example.org/pdf",
        venue_name="Science Robotics",
        venue_tier="first",
        venue_type="journal",
        keywords_matched=["robot learning"],
        recency_score=10.0,
        keyword_score=20.0,
        source_score=20.0,
        total_score=50.0,
    )

    summary = render_release_summary_markdown(
        [paper],
        venue_stats=[{"venue": "Science Robotics", "fetched_count": 3, "filtered_count": 1}],
    )

    assert "Paper Tracker Weekly Report" in summary
    assert "A Robotics Paper" in summary
    assert "Alice, Bob" in summary
    assert "2026-03-24T00:00:00+00:00" in summary
    assert "Science Robotics" in summary
    assert "fetched=3, filtered=1" in summary
    assert "tier=" not in summary
    assert "Score Breakdown" not in summary


def test_candidate_titles_report_lists_titles_only() -> None:
    paper = Paper(
        paper_id="p1",
        title="A Robotics Paper",
        abstract="Detailed abstract.",
        authors=["Alice", "Bob"],
        published_date="2026-03-24T00:00:00+00:00",
        updated_date="2026-03-24T00:00:00+00:00",
        source="openalex",
        primary_category="robotics",
        categories=["robotics"],
        arxiv_url="https://example.org",
        pdf_url="https://example.org/pdf",
        venue_name="Science Robotics",
    )

    content = render_candidate_titles_markdown([paper])

    assert "Candidate Titles Before Keyword Filtering" in content
    assert "1. A Robotics Paper" in content
