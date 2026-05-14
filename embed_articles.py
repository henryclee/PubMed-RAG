import time

import weaviate
from weaviate.util import generate_uuid5

from cache_db.sqlite_utils import retrieve_articles
from core.settings import settings
from embed.embed_utils import build_embedding_text
from embed.embedder import embedder
from vector_db.init_weaviate import init_weaviate

init_weaviate()


start_row_id = 0
client = weaviate.connect_to_local()
collection = client.collections.get("PubMedAbstract")

while True:
    try:
        start = time.time()
        articles = retrieve_articles(
            start_row_id=start_row_id, batch_size=settings.batch_size
        )
        if not articles:
            break
        embedded_texts = build_embedding_text(articles)
        vectors = embedder.embed_batch(embedded_texts)

        with collection.batch.dynamic() as batch:
            for article, vector in zip(articles, vectors):
                batch.add_object(
                    properties={
                        "pmid": article.pmid,
                        "title": article.title,
                        "journal": article.journal,
                        "journal_tier": article.journal_tier,
                        "year": article.year,
                        "abstract_text": article.abstract_text,
                        "background": article.background,
                        "objective": article.objective,
                        "methods": article.methods,
                        "results": article.results,
                        "conclusions": article.conclusions,
                        "publication_types": ", ".join(article.publication_types or []),
                        "keywords": ", ".join(article.keywords or []),
                        "mesh_terms": ", ".join(article.mesh_terms or []),
                    },
                    uuid=generate_uuid5(article.pmid),
                    vector=vector,
                )
        print(
            f"Insertion from row {start_row_id} {len(articles)} objects into Weaviate {time.time() - start:.2f} seconds."
        )
        start_row_id += len(articles)
    except Exception as e:
        print(f"Error processing batch starting at row {start_row_id}: {e}")
        break

client.close()
