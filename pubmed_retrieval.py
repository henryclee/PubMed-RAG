import time

from cache_db.create_tables import create_tables
from cache_db.sqlite_utils import set_retrieval_state, upsert_articles
from pubmed.article_utils import get_articles, search_pmids
from pubmed.journal_utils import get_journals_to_retrieve

if __name__ == "__main__":
    create_tables()

    journals = get_journals_to_retrieve()

    for journal, year in journals:
        print(f"Processing {journal} ({year})...")
        count, pmids = search_pmids(year, journal)
        print(f"Found {count} articles from {journal} in {year}.")
        articles = get_articles(pmids)
        print(
            f"Fetched {len(articles)} articles of total {count}. Upserting into database..."
        )
        upsert_articles(articles)
        set_retrieval_state(journal, year)
        print(f"Completed processing {journal} ({year}).\n")
        time.sleep(1)  # Add a delay between requests to avoid hitting rate limits
