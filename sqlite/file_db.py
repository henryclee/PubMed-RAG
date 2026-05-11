import sqlite3

conn = sqlite3.connect('pubmed_articles.db')
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS articles (
    pmid TEXT PRIMARY KEY,
    title TEXT,
    abstract_structured TEXT,
    journal TEXT,
    year INTEGER,
    month INTEGER
)
""")
conn.commit()
conn.close