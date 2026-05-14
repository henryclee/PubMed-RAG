from huggingface_hub import snapshot_download  # type: ignore


def download_embedding_model() -> None:
    """Run Once to download the embedding model from Hugging Face Hub."""
    snapshot_download(  # type: ignore
        repo_id="BAAI/bge-large-en-v1.5",
        local_dir="/Volumes/Data/embedding_models/bge-large-en-v1.5",
        local_dir_use_symlinks=False,
    )
