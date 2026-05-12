from typing import List, Optional

from pydantic import BaseModel


class Article(BaseModel):
    pmid: str
    doi: str

    title: str
    journal: str
    journal_tier: int
    year: Optional[int] = None
    month: Optional[int] = None

    abstract_text: str = ""
    background: str = ""
    objective: str = ""
    methods: str = ""
    results: str = ""
    conclusions: str = ""
    unassigned: str = ""

    publication_types: List[str] = []
    keywords: List[str] = []
    MeSH_terms: List[str] = []
