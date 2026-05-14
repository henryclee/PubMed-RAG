import os
import sqlite3
from typing import Optional

from core.settings import settings


def create_tables(db_path: Optional[str] = None):

    db_file = db_path or settings.db_path + "/" + settings.db_name

    # Ensure parent directory exists for file-backed DBs
    if db_file != ":memory":
        parent = os.path.dirname(db_file) or "."
        os.makedirs(parent, exist_ok=True)

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        pmid TEXT PRIMARY KEY,
        doi TEXT,
        title TEXT,
        journal TEXT,
        journal_tier INTEGER,
        year INTEGER,
        month INTEGER,
        abstract_text TEXT,
        background TEXT,
        objective TEXT,
        methods TEXT,
        results TEXT,
        conclusions TEXT,
        unassigned TEXT,
        publication_types TEXT,
        keywords TEXT,
        mesh_terms TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS retrieval_state (
        journal TEXT NOT NULL,
        year INTEGER NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (journal, year)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS embedding_state (
        pmid TEXT PRIMARY KEY,
        embedded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
