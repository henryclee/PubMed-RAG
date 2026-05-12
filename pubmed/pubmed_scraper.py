from typing import Any

from Bio import Entrez
from schemas.article import Article
from tracked_journals import JOURNAL_TIERS

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


def get_text(element: Any) -> str:
    """Utility function to extract text from an XML element, handling None values."""
    return str(element).strip() if element is not None else ""


def parse_article(article: Any) -> Article:
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
    title = get_text(article_data.get("ArticleTitle"))

    # ---- Publication Type ----
    publication_type: list[str] = []
    for pt in article_data.get("PublicationTypeList", []):
        publication_type.append(get_text(pt))

    # ---- Keywords ----
    keywords: list[str] = []
    for kw in medline.get("KeywordList", []):
        for k in kw:
            keywords.append(get_text(k))

    # ---- MeSH Terms ----
    mesh_terms: list[str] = []
    for mesh in medline.get("MeshHeadingList", []):
        for m in mesh:
            mesh_terms.append(get_text(m.get("DescriptorName")))

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

    abstract = article_data.get("Abstract", {})
    for part in abstract.get("AbstractText", []):
        label_attr = getattr(part, "attributes", None)
        label = label_attr.get("Label") if label_attr else None
        nlm_category = label_attr.get("NlmCategory") if label_attr else "UNASSIGNED"
        text = get_text(part)
        if label:
            print(label)
            abstract_text += (
                " " + label + ": " + text if abstract_text else label + ": " + text
            )
        else:
            print("UNLABELED")
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

    parsed_article = Article(
        pmid=pmid,
        doi=doi,
        title=title,
        publication_types=publication_type,
        keywords=keywords,
        MeSH_terms=mesh_terms,
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


def get_articles(pmids: list[str]) -> list[Article]:
    """Fetch detailed article information for a list of PMIDs and return as a list of structured Article objects."""
    if not pmids:
        return []

    with Entrez.efetch(db="pubmed", id=",".join(pmids), retmode="xml") as handle:
        records = Entrez.read(handle)

    articles: list[Article] = []

    for article in records.get("PubmedArticle", []):
        article = parse_article(article)
        articles.append(article)

    return articles


def parse_articles_xml(xml_data: str) -> list[dict[str, Any]]:
    # This function can be implemented to parse the XML data if needed.
    # For now, we are using Entrez.read which already returns a structured format.
    return []


def save_articles():
    # This function can be implemented to save articles to a database or file.
    pass


count, pmids = search_pmids(year=2026, journal="Retina")

articles = get_articles(pmids[:1])

for article in articles:
    print(f"PMID: {article.pmid}")
    print(f"DOI: {article.doi}")
    print(f"Title: {article.title}")
    print(f"Journal: {article.journal}")
    print(f"Journal Tier: {article.journal_tier}")
    print(f"Year: {article.year}")
    print(f"Month: {article.month}")
    print(f"Publication Types: {article.publication_types}")
    print(f"Keywords: {article.keywords}")
    print(f"MeSH Terms: {article.MeSH_terms}")
    print(f"Abstract: {article.abstract_text}")
    print("---- Abstract Sections ----")
    if article.background:
        print(f"  BACKGROUND: {article.background}")
    if article.objective:
        print(f"  OBJECTIVE: {article.objective}")
    if article.methods:
        print(f"  METHODS: {article.methods}")
    if article.results:
        print(f"  RESULTS: {article.results}")
    if article.conclusions:
        print(f"  CONCLUSIONS: {article.conclusions}")
    if article.unassigned:
        print(f"  UNASSIGNED: {article.unassigned}")
