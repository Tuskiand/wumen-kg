from pydantic import BaseModel, Field


class AiAnalyzeRequest(BaseModel):
    disease: str
    doctors: list[str]
    node_summary: str
    path_summary: str
    subgraph_summary: str


class AiAnalyzeResponse(BaseModel):
    analysis: str
    model: str


class AiConfigResponse(BaseModel):
    base_url: str
    model: str
    has_key: bool


class AiConfigUpdate(BaseModel):
    api_key: str = ""
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"


class AiConfigTestRequest(BaseModel):
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"


class AiConfigTestResponse(BaseModel):
    success: bool
    message: str