from pydantic import BaseModel, Field

# class Paper(BaseModel):
#     title: str = Field(exclude_none = True)
#     abstract: str = Field(exclude_none = True)
#     github_link: str = Field(exclude_none = True)

# class PaperList(BaseModel):
#     papers: list[Paper] = Field(exclude_none = True)

class Request(BaseModel):
    query: str = Field(exclude_none = True)
    n_results: int = Field(exclude_none = True)