import json
import sqlite3

from core.settings import settings
from schemas.article import Article
from schemas.retrieval_state import RetrievalState


def _connect() -> sqlite3.Connection:
    path = settings.db_path + "/" + settings.db_name
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
            abstract_text, background, objective, methods, results, conclusions,
            unassigned, publication_types, keywords, mesh_terms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        params,
    )


def upsert_articles(articles: list[Article]) -> None:
    """Batch insert or replace multiple articles into the `articles` table."""
    conn = _connect()
    cur = conn.cursor()

    for article in articles:
        _upsert_article(article, cur)

    conn.commit()
    conn.close()


def set_retrieval_state(
    journal: str,
    year: int,
) -> None:
    """Insert or update the retrieval state for a given journal and year."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO retrieval_state (journal, year)
        VALUES (?, ?)
        ON CONFLICT(journal, year) DO UPDATE SET
            updated_at=CURRENT_TIMESTAMP
        """,
        (journal, year),
    )
    conn.commit()
    conn.close()


def get_retrieval_state(journal: str, year: int) -> RetrievalState | None:
    """Fetch the retrieval state for a given journal and year."""
    conn = _connect()
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
