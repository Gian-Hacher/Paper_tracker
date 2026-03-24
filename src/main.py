from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

# Allow running via `python src/main.py` from outside project root.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fetchers.arxiv_fetcher import ArxivFetcher
from src.fetchers.openalex_fetcher import OpenAlexFetcher
from src.processors.dedup import deduplicate_papers
from src.processors.normalize import normalize_paper
from src.processors.select import select_top_papers
from src.processors.venue_filter import filter_and_annotate_by_venue
from src.renderers.markdown_report import write_daily_report
from src.storage.sqlite_store import SQLitePaperStore
from src.utils.logging_utils import setup_logger
from src.utils.venue_utils import VenueMatcher

logger = logging.getLogger(__name__)


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def run_pipeline(
    days_back: int = 365,
    top_n: int = 20,
    project_root: str = ".",
) -> dict[str, str | int]:
    project_path = Path(project_root)
    config_path = project_path / "config"
    keywords_cfg = load_yaml(str(config_path / "keywords.yaml"))
    sources_cfg = load_yaml(str(config_path / "sources.yaml"))
    scoring_cfg = load_yaml(str(config_path / "scoring.yaml"))
    venues_cfg = load_yaml(str(config_path / "venues.yaml"))
    venue_matcher = VenueMatcher(venues_cfg)

    fetched: list = []
    arxiv_cfg = sources_cfg.get("arxiv", {})
    if arxiv_cfg.get("enabled", False):
        arxiv_fetcher = ArxivFetcher(
            endpoint=arxiv_cfg.get("endpoint", "http://export.arxiv.org/api/query"),
            categories=arxiv_cfg.get("categories", ["cs.RO", "cs.AI", "cs.CV"]),
            max_results=int(arxiv_cfg.get("max_results", 200)),
            timeout_seconds=int(arxiv_cfg.get("timeout_seconds", 20)),
        )
        fetched.extend(arxiv_fetcher.fetch(days_back=days_back))

    openalex_cfg = sources_cfg.get("openalex", {})
    if openalex_cfg.get("enabled", False):
        openalex_fetcher = OpenAlexFetcher(
            works_endpoint=openalex_cfg.get("works_endpoint", "https://api.openalex.org/works"),
            sources_endpoint=openalex_cfg.get("sources_endpoint", "https://api.openalex.org/sources"),
            works_per_page=int(openalex_cfg.get("works_per_page", 100)),
            source_lookup_per_page=int(openalex_cfg.get("source_lookup_per_page", 8)),
            timeout_seconds=int(openalex_cfg.get("timeout_seconds", 30)),
            mailto=openalex_cfg.get("mailto", ""),
        )
        source_id_map = openalex_fetcher.resolve_source_ids(venue_matcher.entries, venue_matcher)
        fetched.extend(
            openalex_fetcher.fetch_all_by_sources(
                days_back=days_back,
                source_ids=list(source_id_map.values()),
            )
        )

    normalized = [normalize_paper(paper) for paper in fetched]
    deduped = deduplicate_papers(normalized)
    venue_filtered = filter_and_annotate_by_venue(deduped, venue_matcher)
    strict_filtered, relaxed_filtered, top_papers = select_top_papers(
        papers=venue_filtered,
        include_keywords=keywords_cfg.get("include_keywords", []),
        exclude_keywords=keywords_cfg.get("exclude_keywords", []),
        scoring_config=scoring_cfg,
        top_n=top_n,
    )

    db_path = project_path / "data" / "tracker.db"
    store = SQLitePaperStore(str(db_path))
    inserted_count = store.insert_papers(relaxed_filtered)

    report_path = write_daily_report(
        papers=top_papers,
        output_dir=str(project_path / "outputs" / "daily"),
    )

    result = {
        "fetched": len(fetched),
        "deduped": len(deduped),
        "venue_filtered": len(venue_filtered),
        "filtered": len(strict_filtered),
        "relaxed_filtered": len(relaxed_filtered),
        "selected": len(top_papers),
        "inserted": inserted_count,
        "report_path": report_path,
    }
    logger.info("Pipeline finished: %s", result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paper tracker MVP pipeline")
    parser.add_argument("--days-back", type=int, default=365, help="Fetch papers from last N days")
    parser.add_argument("--top-n", type=int, default=20, help="Top N papers in report")
    parser.add_argument("--project-root", type=str, default=".", help="Project root path")
    return parser.parse_args()


if __name__ == "__main__":
    setup_logger()
    args = parse_args()
    run_pipeline(days_back=args.days_back, top_n=args.top_n, project_root=args.project_root)
