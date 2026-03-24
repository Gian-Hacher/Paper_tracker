from src.models.paper import Paper
from src.processors.venue_filter import filter_and_annotate_by_venue
from src.utils.venue_utils import VenueMatcher


def _paper(venue_raw: str, paper_id: str) -> Paper:
    return Paper(
        paper_id=paper_id,
        title="Robot Manipulation",
        abstract="Embodied policy learning",
        authors=["A"],
        published_date="2026-03-10T00:00:00+00:00",
        updated_date="2026-03-10T00:00:00+00:00",
        source="openalex",
        primary_category="robotics",
        categories=["robotics"],
        arxiv_url="https://example.org",
        pdf_url="https://example.org/pdf",
        venue_raw=venue_raw,
    )


def test_venue_alias_match_cvpr() -> None:
    cfg = {
        "conferences": [
            {
                "canonical_name": "IEEE Conference on Computer Vision and Pattern Recognition",
                "aliases": ["CVPR"],
                "tier": "first",
                "type": "conference",
            }
        ],
        "journals": [],
    }
    matcher = VenueMatcher(cfg)
    result = filter_and_annotate_by_venue([_paper("cvpr", "1")], matcher)
    assert len(result) == 1
    assert result[0].venue_name == "IEEE Conference on Computer Vision and Pattern Recognition"


def test_venue_alias_match_cvpr_with_suffix() -> None:
    cfg = {
        "conferences": [
            {
                "canonical_name": "IEEE Conference on Computer Vision and Pattern Recognition",
                "aliases": ["CVPR"],
                "tier": "first",
                "type": "conference",
            }
        ],
        "journals": [],
    }
    matcher = VenueMatcher(cfg)
    result = filter_and_annotate_by_venue([_paper("Proceedings of CVPR 2025", "2")], matcher)
    assert len(result) == 1
    assert result[0].venue_name == "IEEE Conference on Computer Vision and Pattern Recognition"


def test_venue_alias_match_long_variant() -> None:
    cfg = {
        "conferences": [
            {
                "canonical_name": "IEEE/RSJ International Conference on Intelligent Robots and Systems",
                "aliases": ["IROS"],
                "tier": "first",
                "type": "conference",
            }
        ],
        "journals": [],
    }
    matcher = VenueMatcher(cfg)
    result = filter_and_annotate_by_venue(
        [
            _paper(
                "Proceedings of the IEEE RSJ International Conference on Intelligent Robots and Systems",
                "3",
            )
        ],
        matcher,
    )
    assert len(result) == 1
    assert result[0].venue_name == "IEEE/RSJ International Conference on Intelligent Robots and Systems"


def test_venue_unknown_is_dropped() -> None:
    cfg = {"conferences": [], "journals": []}
    matcher = VenueMatcher(cfg)
    result = filter_and_annotate_by_venue([_paper("Unknown Venue", "1")], matcher)
    assert len(result) == 0


def test_no_reverse_containment_false_positive() -> None:
    cfg = {
        "conferences": [
            {
                "canonical_name": "Robotics: Science and Systems",
                "aliases": ["RSS"],
                "tier": "first",
                "type": "conference",
            }
        ],
        "journals": [],
    }
    matcher = VenueMatcher(cfg)
    result = filter_and_annotate_by_venue([_paper("Robotics", "4")], matcher)
    assert len(result) == 0
