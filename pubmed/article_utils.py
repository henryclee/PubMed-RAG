from typing import Any

from Bio import Entrez

from core.settings import settings
from pubmed.tracked_journals import JOURNAL_TIERS
from schemas.article import Article

Entrez.email = settings.entrez_email
Entrez.tool = settings.entrez_tool

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


def search_pmids(
    year: int, journal: str, batch_size: int = 200
) -> tuple[int, list[str]]:
    """Search PubMed for articles from a specific journal and year, returning the count and list of PMIDs."""

    term = f'"{journal}"[ta] AND {year}[pdat]'
    pmids: list[str] = []
    start = 0

    while True:
        with Entrez.esearch(
            db="pubmed", term=term, retstart=start, retmax=batch_size
        ) as handle:
            raw = Entrez.read(handle)

        batch_pmids = raw.get("IdList", [])
        if not batch_pmids:
            break

        pmids.extend(batch_pmids)

        if len(batch_pmids) < batch_size:
            break

        start += batch_size

    count = len(pmids)
    return count, pmids


def _get_text(element: Any) -> str:
    """Utility function to extract text from an XML element, handling None values."""
    return str(element).strip() if element is not None else ""


def parse_article(article: Any) -> Article | None:
    """Parse a single article record from PubMed XML into a structured Article object."""
    medline = article["MedlineCitation"]
    article_data = medline["Article"]
    pmid = str(medline["PMID"])

    # ---- DOI ----
    doi = ""
    for aid in article.get("PubmedData", {}).get("ArticleIdList", []):
        if getattr(aid, "attributes", {}).get("IdType") == "doi":
            doi = str(aid)

    # ---- Title ----
    title = _get_text(article_data.get("ArticleTitle"))

    # ---- Publication Type ----
    publication_type: list[str] = []
    for pt in article_data.get("PublicationTypeList", []):
        publication_type.append(_get_text(pt))

    # ---- Keywords ----
    keywords: list[str] = []
    for kw in medline.get("KeywordList", []):
        for k in kw:
            keywords.append(_get_text(k))

    # ---- MeSH Terms ----
    mesh_terms: list[str] = []
    for mesh in medline.get("MeshHeadingList", []):
        # Entrez may return dicts, lists, or sequence-like objects for MeshHeading entries.
        # If `mesh` is a dict, read DescriptorName/QualifierName directly; otherwise
        # try iterating elements and handle dicts/strings/objects robustly.
        if isinstance(mesh, dict):
            descriptor = mesh.get("DescriptorName", None)  # type: ignore
            if descriptor and descriptor.attributes.get("MajorTopicYN") == "Y":  # type: ignore
                mesh_terms.append(_get_text(descriptor))
        else:
            for m in mesh:
                if isinstance(m, dict):
                    descriptor = m.get("DescriptorName", None)  # type: ignore
                    if descriptor and descriptor.attributes.get("MajorTopicYN") == "Y":  # type: ignore
                        mesh_terms.append(_get_text(descriptor))

    # ---- Abstract ----
    abstract_text = ""
    abstract_blocks = {
        "BACKGROUND": "",
        "OBJECTIVE": "",
        "METHODS": "",
        "RESULTS": "",
        "CONCLUSIONS": "",
        "UNASSIGNED": "",
    }

    label_nlm_category_map = {
        "BACKGROUND": "BACKGROUND",
        "BACKGROUND/PURPOSE": "OBJECTIVE",
        "PURPOSE": "OBJECTIVE",
        "OBJECTIVE": "OBJECTIVE",
        "METHOD": "METHODS",
        "METHODS": "METHODS",
        "RESULT": "RESULTS",
        "RESULTS": "RESULTS",
        "CONCLUSION": "CONCLUSIONS",
        "CONCLUSIONS": "CONCLUSIONS",
    }

    abstract = article_data.get("Abstract", {})
    for part in abstract.get("AbstractText", []):
        label_attr = getattr(part, "attributes", None)

        label = None
        nlm_category = None

        if label_attr:
            label = label_attr.get("Label")
            nlm_category = label_attr.get("NlmCategory") or label_nlm_category_map.get(
                label, "UNASSIGNED"
            )

        text = _get_text(part)
        if label:
            abstract_text += (
                " " + label + ": " + text if abstract_text else label + ": " + text
            )
        else:
            abstract_text += " " + text if abstract_text else text

        if nlm_category not in abstract_blocks:
            nlm_category = "UNASSIGNED"

        abstract_blocks[nlm_category] += (
            " " + text if abstract_blocks[nlm_category] else text
        )

    # ---- Journal ----
    journal = ""
    j = article_data.get("Journal", {})

    journal = j.get("ISOAbbreviation") or j.get("MedlineTA") or j.get("Title", "")

    # ---- Date ----
    year = None
    month = None

    pub_date = j.get("JournalIssue", {}).get("PubDate", {})

    if "Year" in pub_date:
        year = int(pub_date["Year"])

    if "Month" in pub_date:
        month = month_map.get(pub_date["Month"])

    # If there is no abstract text, return None
    if abstract_text == "":
        return None

    parsed_article = Article(
        pmid=pmid,
        doi=doi,
        title=title,
        publication_types=publication_type,
        keywords=keywords,
        mesh_terms=mesh_terms,
        journal_tier=JOURNAL_TIERS.get(journal, 3),
        abstract_text=abstract_text,
        background=abstract_blocks["BACKGROUND"],
        objective=abstract_blocks["OBJECTIVE"],
        methods=abstract_blocks["METHODS"],
        results=abstract_blocks["RESULTS"],
        conclusions=abstract_blocks["CONCLUSIONS"],
        unassigned=abstract_blocks["UNASSIGNED"],
        journal=journal,
        year=year,
        month=month,
    )

    return parsed_article


def get_articles(pmids: list[str], batch_size: int = 200) -> list[Article]:
    """Fetch detailed article information for a list of PMIDs and return as a list of structured Article objects."""
    if not pmids:
        return []

    articles: list[Article] = []
    start = 0

    while True:
        batch_pmids = pmids[start : start + batch_size]

        with Entrez.efetch(
            db="pubmed", id=",".join(batch_pmids), retmode="xml"
        ) as handle:
            records = Entrez.read(handle)

        for article in records.get("PubmedArticle", []):
            article = parse_article(article)
            if article:
                articles.append(article)

        start += batch_size
        if start >= len(pmids):
            break

    return articles
