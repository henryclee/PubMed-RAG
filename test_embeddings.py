import weaviate

from embed.embedder import embedder

client = weaviate.connect_to_local()
collection = client.collections.get("PubMedAbstract")

query = "intracranial pressure optic nerve swelling papilledema"
query_vector = embedder.embed(query)

results = collection.query.near_vector(
    near_vector=query_vector,
    limit=5,
)

for r in results.objects:
    print(f"PMID: {r.properties['pmid']}")
    print(f"Title: {r.properties['title']}")
    print(f"Journal: {r.properties['journal']}")
    print(f"Year: {r.properties['year']}")
    print(f"Abstract: {r.properties['abstract_text']}...")
    print("-" * 80)
client.close()
