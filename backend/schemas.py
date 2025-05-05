from pydantic import BaseModel, Field

class Request(BaseModel):
    query: str = Field(exclude_none = True)
    n_results: int = Field(exclude_none = True)