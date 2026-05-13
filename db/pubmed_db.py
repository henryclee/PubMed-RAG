import json
import sqlite3

from schemas.article import Article
from schemas.retrieval_state import RetrievalState

DB_PATH_DEFAULT = "pubmed_articles.db"


def _connect(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH_DEFAULT
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _upsert_article(article: Article, cur: sqlite3.Cursor) -> None:
    """Insert or replace an article into the `articles` table.
    Accepts an Article object
    Lists are stored as JSON strings.
    """

    publication_types = json.dumps(article.publication_types or [])
    keywords = json.dumps(article.keywords or [])
    mesh_terms = json.dumps(article.MeSH_terms or [])

    params = (
        article.pmid,
        article.doi,
        article.title,
        article.journal,
        article.journal_tier,
        article.year,
        article.month,
        article.abstract_text,
        article.background,
        article.objective,
        article.methods,
        article.results,
        article.conclusions,
        article.unassigned,
        publication_types,
        keywords,
        mesh_terms,
    )

    cur.execute(
        """
        INSERT OR REPLACE INTO articles (
            pmid, doi, title, journal, journal_tier, year, month,
            abstract, background, objective, methods, results, conclusions,
            unassigned, publication_types, keywords, mesh_terms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        params,
    )


def upsert_articles(articles: list[Article], db_path: str | None = None) -> None:
    """Batch insert or replace multiple articles into the `articles` table."""
    conn = _connect(db_path)
    cur = conn.cursor()

    for article in articles:
        _upsert_article(article, cur)

    conn.commit()
    conn.close()


def set_retrieval_state(
    journal: str,
    year: int,
    status: str,
    total_expected: int | None = None,
    total_fetched: int | None = None,
    db_path: str | None = None,
) -> None:
    """Insert or update the retrieval state for a given journal and year."""
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO retrieval_state (journal, year, status, total_expected, total_fetched)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(journal, year) DO UPDATE SET
            status=excluded.status,
            total_expected=COALESCE(excluded.total_expected, retrieval_state.total_expected),
            total_fetched=COALESCE(excluded.total_fetched, retrieval_state.total_fetched),
            updated_at=CURRENT_TIMESTAMP
        """,
        (journal, year, status, total_expected, total_fetched),
    )
    conn.commit()
    conn.close()


def get_retrieval_state(
    journal: str, year: int, db_path: str | None = None
) -> RetrievalState | None:
    """Fetch the retrieval state for a given journal and year."""
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM retrieval_state WHERE journal = ? AND year = ?", (journal, year)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return RetrievalState(**dict(row))
    else:
        return None
