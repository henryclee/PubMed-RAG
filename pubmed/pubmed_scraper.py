from typing import Any, Dict, List, cast

from Bio import Entrez

Entrez.email = "henryclee73@gmail.com"
Entrez.tool = "local_pubmed_rag"

month_map = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def get_pmids(year: int, journal: str, retmax: int = 20) -> List[str]:
    term = f'"{journal}"[Journal] AND {year}[pdat]'
    with cast(Any, Entrez.esearch(db="pubmed", term=term, retmax=retmax)) as handle:
        raw = Entrez.read(handle)
    record = cast(Dict[str, Any], raw)
    pmids = cast(List[str], record.get("IdList", []))
    if "IdList" not in record or not isinstance(record["IdList"], list):
        raise ValueError("Unexpected record format")
    return pmids


def get_articles(pmids: List[str]) -> List[Dict[str, Any]]:
    if not pmids:
        return []
    with cast(
        Any,
        Entrez.efetch(
            db="pubmed",
            id=",".join(pmids),
            retmode="xml",
        ),
    ) as handle:
        raw = Entrez.read(handle)

    records = cast(Dict[str, Any], raw)

    articles: list[dict[str, Any]] = []

    for article in cast(List[Dict[str, Any]], records.get("PubmedArticle", [])):
        medline = cast(Dict[str, Any], article.get("MedlineCitation", {}))
        article_data = cast(Dict[str, Any], medline.get("Article", {}))

        pmid = str(medline["PMID"])
        keywordlist = medline.get("KeywordList", [])
        keywords: list[str] = []
        for keyword_group in keywordlist:
            for keyword in keyword_group:
                keywords.append(str(keyword))

        title = str(article_data.get("ArticleTitle", ""))

        abstract_text: dict[str, str] = {}

        abstract = article_data.get("Abstract")
        if abstract and "AbstractText" in abstract:
            for part in abstract["AbstractText"]:
                nlm_category = part.attributes.get("NlmCategory")
                abstract_text[nlm_category] = abstract_text.get(nlm_category, "") + str(
                    part
                )

        journal = ""
        journal_info = article_data.get("Journal")
        if journal_info and "Title" in journal_info:
            journal = str(journal_info["Title"])

        pub_date = None
        pub_year = None
        pub_month = None
        if journal_info and "JournalIssue" in journal_info:
            issue = journal_info["JournalIssue"]
            if "PubDate" in issue:
                pub_date = issue["PubDate"]
                if "Year" in pub_date:
                    pub_year = int(pub_date["Year"])
                if "Month" in pub_date:
                    pub_month = month_map.get(pub_date["Month"], None)

        articles.append(
            {
                "pmid": pmid,
                "title": title,
                "abstract": abstract_text,
                "journal": journal,
                "year": pub_year,
                "month": pub_month,
                "keywords": keywords,
            }
        )

    return articles


pmids = get_pmids(2026, "Retina", retmax=2)
print("PMIDs:", pmids)

articles = get_articles(pmids)

for k, v in articles[0].items():
    print(f"{k}: {v}")
