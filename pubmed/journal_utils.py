from datetime import datetime

from cache_db.sqlite_utils import get_retrieval_state
from pubmed.tracked_journals import OPHTH_JOURNALS


def get_journals_to_retrieve() -> list[tuple[str, int]]:
    """Determine which journals and years need to be retrieved based on the retrieval state."""
    journals_to_retrieve: list[tuple[str, int]] = []
    current_year = datetime.now().year

    for _, journals in OPHTH_JOURNALS.items():
        for journal in journals:
            for year in range(current_year, 2014, -1):
                state = get_retrieval_state(journal, year)
                if state is None:
                    journals_to_retrieve.append((journal, year))

    return journals_to_retrieve
