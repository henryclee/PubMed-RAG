from typing import Any

WEAVIATE_SCHEMA: dict[str, Any] = {
    "class": "PubMedArticle",
    "vectorizer": "none",
    "properties": [
        {"name": "pmid", "dataType": ["text"]},
        {"name": "title", "dataType": ["text"]},
        {"name": "abstract", "dataType": ["text"]},
        {"name": "journal", "dataType": ["text"]},
        {"name": "year", "dataType": ["int"]},
    ],
}
