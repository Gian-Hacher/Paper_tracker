from __future__ import annotations

from datetime import datetime, timezone

from src.models.paper import Paper


def _safe_parse_date(date_text: str) -> datetime | None:
    try:
        return datetime.fromisoformat(date_text.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_recency_score(
    published_date: str,
    window_days: int,
    max_score: float,
) -> float:
    published = _safe_parse_date(published_date)
    if published is None:
        return 0.0

    now = datetime.now(timezone.utc)
    age_days = max((now - published).days, 0)
    if age_days >= window_days:
        return 0.0

    ratio = (window_days - age_days) / window_days
    return round(ratio * max_score, 4)


def compute_keyword_score(
    matched_keywords: list[str],
    max_hits: int,
    max_score: float,
) -> float:
    hit_count = min(len(set(matched_keywords)), max_hits)
    if max_hits <= 0:
        return 0.0
    return round((hit_count / max_hits) * max_score, 4)


def compute_source_score(
    source: str,
    source_scores: dict[str, float],
    default_score: float,
) -> float:
    return float(source_scores.get(source, default_score))


def score_paper(paper: Paper, scoring_config: dict) -> Paper:
    recency_cfg = scoring_config["recency"]
    keyword_cfg = scoring_config["keyword"]
    source_cfg = scoring_config["source"]
    weights_cfg = scoring_config.get("weights", {})
    future_cfg = scoring_config.get("future_scores", {})

    paper.recency_score = compute_recency_score(
        paper.published_date,
        window_days=int(recency_cfg["window_days"]),
        max_score=float(recency_cfg["max_score"]),
    )
    paper.keyword_score = compute_keyword_score(
        paper.keywords_matched,
        max_hits=int(keyword_cfg["max_hits"]),
        max_score=float(keyword_cfg["max_score"]),
    )
    paper.source_score = compute_source_score(
        paper.source,
        source_scores=source_cfg.get("source_scores", {}),
        default_score=float(source_cfg.get("default_score", 0.0)),
    )

    total = (
        paper.recency_score * float(weights_cfg.get("recency_weight", 1.0))
        + paper.keyword_score * float(weights_cfg.get("keyword_weight", 1.0))
        + paper.source_score * float(weights_cfg.get("source_weight", 1.0))
        + float(future_cfg.get("venue_score", 0.0))
        + float(future_cfg.get("citation_score", 0.0))
        + float(future_cfg.get("code_score", 0.0))
    )
    paper.total_score = round(total, 4)
    return paper


def score_papers(papers: list[Paper], scoring_config: dict) -> list[Paper]:
    return [score_paper(paper, scoring_config) for paper in papers]

