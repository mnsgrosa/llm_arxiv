from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

class MetadataTitle(BaseModel):
    paper_url: str = Field(exclude_none = True)
    github_url: Optional[str] = None
    document_type: str = 'title'
    title: str = Field(exclude_none = True)
    paper_id: str = Field(exclude_none = True) 

class Title(BaseModel):
    ids: str = Field(exclude_none = True)
    documents: str = Field(exclude_none = True)
    metadatas: MetadataTitle = Field(exclude_none = True)

class MetadataAbstract(BaseModel):
    paper_url: str = Field(exclude_none = True)
    github_url: Optional[str] = None
    document_type: str = 'abstract'
    abstract: Optional[str] = None
    paper_id: str = Field(exclude_none = True) 

class Abstract(BaseModel):
    ids: str = Field(exclude_none = True)
    documents: Optional[str] = None
    metadatas: MetadataAbstract = Field(exclude_none = True)

class Getter(BaseModel):
    query: str = Field(exclude_none = True)
    n_results: Optional[int] = 5

class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

class ToolInfo(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolsResponse(BaseModel):
    tools: List[ToolInfo]

class ToolCallResponse(BaseModel):
    content: Any
    isError: bool = False

class ScrapeRequest(BaseModel):
    topic: str
    max_results: int = 10

class SearchRequest(BaseModel):
    topic: str
    max_results: int = 10

class GetOrScrapeRequest(BaseModel):
    topic: str
    max_results: int = 10

class ListTopicsRequest(BaseModel):
    limit: int = 20

class StandardResponse(BaseModel):
    data: Any
    error: Optional[str] = None
    success: bool = True