from pydantic import BaseModel

class SPARQLResponse(BaseModel):
    dataset: str
    question: str
    query: str
