from src.models.paper import Paper
from src.processors.dedup import deduplicate_papers


def make_paper(paper_id: str, title: str) -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        abstract="test",
        authors=["A"],
        published_date="2026-03-10T00:00:00+00:00",
        updated_date="2026-03-10T00:00:00+00:00",
        source="arxiv",
        primary_category="cs.RO",
        categories=["cs.RO"],
        arxiv_url="https://arxiv.org/abs/1111.1111",
        pdf_url="https://arxiv.org/pdf/1111.1111.pdf",
    )


def test_dedup_removes_duplicate_id_and_title() -> None:
    papers = [
        make_paper("id-1", "A Robot Manipulation Paper"),
        make_paper("id-1", "A Robot Manipulation Paper"),
        make_paper("id-2", "A  Robot   Manipulation   Paper"),
        make_paper("id-3", "Another Embodied AI Paper"),
    ]
    result = deduplicate_papers(papers)
    assert len(result) == 2
    assert result[0].paper_id == "id-1"
    assert result[1].paper_id == "id-3"

