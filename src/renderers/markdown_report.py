from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.models.paper import Paper


def _render_venue_stats(venue_stats: list[dict[str, int | str]] | None) -> list[str]:
    if not venue_stats:
        return []
    lines = [
        "## Venue Statistics",
        "",
    ]
    for item in venue_stats:
        lines.append(
            f"- {item['venue']}: fetched={item['fetched_count']}, filtered={item['filtered_count']}"
        )
    lines.append("")
    return lines


def render_daily_markdown(
    papers: list[Paper],
    report_date: datetime | None = None,
    venue_stats: list[dict[str, int | str]] | None = None,
) -> str:
    report_date = report_date or datetime.now()
    date_text = report_date.strftime("%Y-%m-%d")
    lines: list[str] = [
        f"# Paper Tracker Daily Report ({date_text})",
        "",
        f"Total selected papers: **{len(papers)}**",
        "",
    ]
    lines.extend(_render_venue_stats(venue_stats))

    for index, paper in enumerate(papers, start=1):
        lines.extend(
            [
                f"## {index}. {paper.title}",
                "",
                f"- Authors: {', '.join(paper.authors) if paper.authors else 'N/A'}",
                f"- Published: {paper.published_date}",
                f"- Source: {paper.source}",
                f"- Venue: {paper.venue_name or paper.venue_raw or 'Unknown'} ({paper.venue_type or 'unknown'}, tier={paper.venue_tier or 'unknown'})",
                f"- Primary URL: {paper.arxiv_url}",
                f"- PDF: {paper.pdf_url}",
                f"- Matched Keywords: {', '.join(paper.keywords_matched) if paper.keywords_matched else 'None'}",
                (
                    "- Score Breakdown: "
                    f"recency={paper.recency_score:.2f}, "
                    f"keyword={paper.keyword_score:.2f}, "
                    f"source={paper.source_score:.2f}, "
                    f"total={paper.total_score:.2f}"
                ),
                "",
                "### Abstract",
                paper.abstract or "N/A",
                "",
            ]
        )
    return "\n".join(lines)


def render_release_summary_markdown(
    papers: list[Paper],
    report_date: datetime | None = None,
    venue_stats: list[dict[str, int | str]] | None = None,
) -> str:
    report_date = report_date or datetime.now()
    date_text = report_date.strftime("%Y-%m-%d")
    lines: list[str] = [
        f"# Paper Tracker Weekly Report ({date_text})",
        "",
        f"Total selected papers: **{len(papers)}**",
        "",
    ]
    lines.extend(_render_venue_stats(venue_stats))

    for index, paper in enumerate(papers, start=1):
        lines.extend(
            [
                f"## {index}. {paper.title}",
                f"- Authors: {', '.join(paper.authors) if paper.authors else 'N/A'}",
                f"- Published: {paper.published_date}",
                f"- Venue: {paper.venue_name or paper.venue_raw or 'Unknown'}",
                "",
            ]
        )

    return "\n".join(lines)


def write_daily_report(
    papers: list[Paper],
    output_dir: str,
    report_date: datetime | None = None,
    venue_stats: list[dict[str, int | str]] | None = None,
) -> str:
    report_date = report_date or datetime.now()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"{report_date.strftime('%Y-%m-%d')}.md"
    output_file.write_text(
        render_daily_markdown(papers, report_date, venue_stats),
        encoding="utf-8",
    )
    return str(output_file)


def write_release_summary(
    papers: list[Paper],
    output_dir: str,
    report_date: datetime | None = None,
    venue_stats: list[dict[str, int | str]] | None = None,
) -> str:
    report_date = report_date or datetime.now()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"weekly-summary-{report_date.strftime('%Y-%m-%d')}.md"
    output_file.write_text(
        render_release_summary_markdown(papers, report_date, venue_stats),
        encoding="utf-8",
    )
    return str(output_file)


def write_candidate_titles_report(
    papers: list[Paper],
    output_dir: str,
    report_date: datetime | None = None,
) -> str:
    report_date = report_date or datetime.now()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"candidate-titles-{report_date.strftime('%Y-%m-%d')}.md"

    output_file.write_text(
        render_candidate_titles_markdown(papers, report_date),
        encoding="utf-8",
    )
    return str(output_file)


def render_candidate_titles_markdown(
    papers: list[Paper],
    report_date: datetime | None = None,
) -> str:
    report_date = report_date or datetime.now()
    lines: list[str] = [
        f"# Candidate Titles Before Keyword Filtering ({report_date.strftime('%Y-%m-%d')})",
        "",
        f"Total candidates: **{len(papers)}**",
        "",
    ]

    for index, paper in enumerate(papers, start=1):
        lines.append(f"{index}. {paper.title}")

    return "\n".join(lines)
