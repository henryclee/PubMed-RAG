from pydantic import BaseModel


class RetrievalState(BaseModel):
    journal: str
    year: int
    total_expected: int
    total_fetched: int
