import weaviate
import weaviate.classes as wvc


def init_weaviate():
    client = weaviate.connect_to_local()

    if not client.collections.exists("PubMedAbstract"):
        client.collections.create(
            name="PubMedAbstract",
            vectorizer_config=None,
            properties=[
                wvc.config.Property(name="pmid", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="journal", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(
                    name="journal_tier", data_type=wvc.config.DataType.INT
                ),
                wvc.config.Property(name="year", data_type=wvc.config.DataType.INT),
                wvc.config.Property(
                    name="abstract_text", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="background", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="objective", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(name="methods", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="results", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(
                    name="conclusions", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="publication_types", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="keywords", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="mesh_terms", data_type=wvc.config.DataType.TEXT
                ),
            ],
        )
        print("Created Weaviate collection 'PubMedAbstract'")
    else:
        print("Weaviate collection 'PubMedAbstract' already exists")

    client.close()
