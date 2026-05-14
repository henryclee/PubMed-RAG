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
    mesh_terms = json.dumps(article.mesh_terms or [])

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


def retrieve_articles(start_row_id: int, batch_size: int) -> list[Article]:
    """Fetch a batch of articles from the `articles` table starting from a specific row ID."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * 
        FROM articles a
        WHERE rowid > ? 
        AND NOT EXISTS (
            SELECT 1
            FROM embedding_state e
            WHERE e.pmid = a.pmid
        )
        ORDER BY rowid 
        LIMIT ?
        """,
        (start_row_id, batch_size),
    )
    rows = cur.fetchall()
    conn.close()

    articles: list[Article] = []
    for row in rows:
        article_dict = dict(row)
        article_dict["publication_types"] = json.loads(
            article_dict["publication_types"]
        )
        article_dict["keywords"] = json.loads(article_dict["keywords"])
        article_dict["mesh_terms"] = json.loads(article_dict["mesh_terms"])
        articles.append(Article(**article_dict))

    return articles


def mark_articles_embedded(pmids: list[str]) -> None:
    """Batch mark multiple articles as embedded."""
    conn = _connect()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT OR REPLACE INTO embedding_state (pmid)
        VALUES (?)
        """,
        [(pmid,) for pmid in pmids],
    )
    conn.commit()
    conn.close()
