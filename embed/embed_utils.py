from schemas.article import Article


def build_embedding_text(articles: list[Article]) -> list[str]:
    """Build the text to be embedded for a list of articles."""
    texts: list[str] = []
    for article in articles:
        parts = [f"TITLE: {article.title}"]
        if article.objective:
            parts.append(f"OBJECTIVE: {article.objective}")
        if article.conclusions:
            parts.append(f"CONCLUSIONS: {article.conclusions}")
        if article.keywords:
            parts.append(f"KEYWORDS: {', '.join(article.keywords)}")
        if article.mesh_terms:
            parts.append(f"MeSH TERMS: {', '.join(article.mesh_terms)}")
        texts.append("\n".join(parts))
    return texts
