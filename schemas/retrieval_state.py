import datetime

from pydantic import BaseModel


class RetrievalState(BaseModel):
    journal: str
    year: int
    updated_at: datetime.datetime
