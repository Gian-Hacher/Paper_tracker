from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from src.models.paper import Paper


class SQLitePaperStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    abstract TEXT NOT NULL,
                    authors_json TEXT NOT NULL,
                    published_date TEXT NOT NULL,
                    updated_date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    primary_category TEXT,
                    categories_json TEXT NOT NULL,
                    arxiv_url TEXT,
                    pdf_url TEXT,
                    venue_raw TEXT,
                    venue_name TEXT,
                    venue_tier TEXT,
                    venue_type TEXT,
                    keywords_matched_json TEXT NOT NULL,
                    recency_score REAL NOT NULL,
                    keyword_score REAL NOT NULL,
                    source_score REAL NOT NULL,
                    total_score REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._ensure_columns(conn)

    @staticmethod
    def _ensure_columns(conn: sqlite3.Connection) -> None:
        required_columns = {
            "venue_raw": "TEXT",
            "venue_name": "TEXT",
            "venue_tier": "TEXT",
            "venue_type": "TEXT",
        }
        rows = conn.execute("PRAGMA table_info(papers)").fetchall()
        existing = {row[1] for row in rows}
        for col, col_type in required_columns.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE papers ADD COLUMN {col} {col_type}")

    def insert_papers(self, papers: list[Paper]) -> int:
        inserted = 0
        with self._connect() as conn:
            for paper in papers:
                result = conn.execute(
                    """
                    INSERT OR IGNORE INTO papers (
                        paper_id, title, abstract, authors_json, published_date, updated_date,
                        source, primary_category, categories_json, arxiv_url, pdf_url,
                        venue_raw, venue_name, venue_tier, venue_type,
                        keywords_matched_json, recency_score, keyword_score, source_score, total_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        paper.paper_id,
                        paper.title,
                        paper.abstract,
                        json.dumps(paper.authors, ensure_ascii=False),
                        paper.published_date,
                        paper.updated_date,
                        paper.source,
                        paper.primary_category,
                        json.dumps(paper.categories, ensure_ascii=False),
                        paper.arxiv_url,
                        paper.pdf_url,
                        paper.venue_raw,
                        paper.venue_name,
                        paper.venue_tier,
                        paper.venue_type,
                        json.dumps(paper.keywords_matched, ensure_ascii=False),
                        paper.recency_score,
                        paper.keyword_score,
                        paper.source_score,
                        paper.total_score,
                    ),
                )
                if result.rowcount > 0:
                    inserted += 1
        return inserted

    def get_top_papers(self, top_n: int = 10) -> list[Paper]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT
                    paper_id, title, abstract, authors_json, published_date, updated_date,
                    source, primary_category, categories_json, arxiv_url, pdf_url,
                    venue_raw, venue_name, venue_tier, venue_type,
                    keywords_matched_json, recency_score, keyword_score, source_score, total_score
                FROM papers
                WHERE COALESCE(venue_name, '') != ''
                ORDER BY total_score DESC, published_date DESC
                LIMIT ?
                """,
                (top_n,),
            )
            rows = cursor.fetchall()

        papers: list[Paper] = []
        for row in rows:
            papers.append(
                Paper(
                    paper_id=row[0],
                    title=row[1],
                    abstract=row[2],
                    authors=json.loads(row[3]),
                    published_date=row[4],
                    updated_date=row[5],
                    source=row[6],
                    primary_category=row[7],
                    categories=json.loads(row[8]),
                    arxiv_url=row[9],
                    pdf_url=row[10],
                    venue_raw=row[11] or "",
                    venue_name=row[12] or "",
                    venue_tier=row[13] or "",
                    venue_type=row[14] or "",
                    keywords_matched=json.loads(row[15]),
                    recency_score=row[16],
                    keyword_score=row[17],
                    source_score=row[18],
                    total_score=row[19],
                )
            )
        return papers
