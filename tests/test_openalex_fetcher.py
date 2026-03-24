from src.fetchers.openalex_fetcher import OpenAlexFetcher, _extract_openalex_id


def test_extract_openalex_id_from_url() -> None:
    assert _extract_openalex_id("https://openalex.org/S123456789") == "S123456789"


def test_source_candidate_names_collect_known_fields() -> None:
    source = {
        "display_name": "IEEE Conference on Computer Vision and Pattern Recognition",
        "abbreviated_title": "CVPR",
        "alternate_titles": ["IEEE CVPR"],
    }
    names = OpenAlexFetcher._source_candidate_names(source)
    assert "IEEE Conference on Computer Vision and Pattern Recognition" in names
    assert "CVPR" in names
    assert "IEEE CVPR" in names


def test_fetch_all_by_sources_returns_empty_when_no_source_ids() -> None:
    fetcher = OpenAlexFetcher(
        works_endpoint="https://api.openalex.org/works",
        sources_endpoint="https://api.openalex.org/sources",
    )
    assert fetcher.fetch_all_by_sources(days_back=30, source_ids=[]) == []
