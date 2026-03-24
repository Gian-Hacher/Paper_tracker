from src.models.paper import Paper
from src.processors.filter import filter_papers


def make_paper(title: str, abstract: str, paper_id: str = "1") -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        abstract=abstract,
        authors=["A"],
        published_date="2026-03-10T00:00:00+00:00",
        updated_date="2026-03-10T00:00:00+00:00",
        source="arxiv",
        primary_category="cs.RO",
        categories=["cs.RO"],
        arxiv_url="https://arxiv.org/abs/1234.5678",
        pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
    )


def test_filter_keeps_embodied_manipulation_paper() -> None:
    papers = [make_paper("Embodied AI for Robot Manipulation", "A new manipulation policy.")]
    result = filter_papers(
        papers,
        include_keywords=["embodied ai", "manipulation"],
        exclude_keywords=["autonomous driving"],
    )
    assert len(result) == 1
    assert "embodied ai" in [kw.lower() for kw in result[0].keywords_matched]


def test_filter_excludes_noise_topic() -> None:
    papers = [make_paper("Autonomous Driving Planner", "A driving benchmark.")]
    result = filter_papers(
        papers,
        include_keywords=["policy learning"],
        exclude_keywords=["autonomous driving"],
    )
    assert len(result) == 0


def test_filter_can_keep_search_results_without_local_keyword_hit() -> None:
    papers = [make_paper("A Relevant Paper", "Uses learned action representations.")]
    result = filter_papers(
        papers,
        include_keywords=["robot manipulation"],
        exclude_keywords=["autonomous driving"],
        require_include_match=False,
    )
    assert len(result) == 1
    assert result[0].keywords_matched == []
