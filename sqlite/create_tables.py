import sqlite3

conn = sqlite3.connect("pubmed_articles.db")
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
    abstract TEXT,
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

    status TEXT NOT NULL, 
    -- "pending" | "in_progress" | "complete" | "failed"
    total_expected INTEGER,
    total_fetched INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (journal, year)
)
""")

conn.commit()
conn.close()
