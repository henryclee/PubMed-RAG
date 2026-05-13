from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    db_name: str = "pubmed_articles.db"
    db_path: str = "./db"
    db_uri: str = f"sqlite:///{db_path}/{db_name}"
    entrez_email: str = "henryclee73@gmail.com"
    entrez_tool: str = "local_pubmed_rag"


settings = Settings()
