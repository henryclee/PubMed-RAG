from typing import Any, ContextManager

# Minimal stubs for the parts of Bio.Entrez used in this project.

email: str
tool: str

def esearch(db: str, term: str, retmax: int = ...) -> ContextManager[Any]: ...
def efetch(
    db: str, id: str, retmode: str = ..., **kwargs: Any
) -> ContextManager[Any]: ...
def read(handle: Any) -> Any: ...
