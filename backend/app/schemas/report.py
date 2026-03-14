from pydantic import BaseModel
from typing import List, Any


class ReportResponse(BaseModel):
    task_id: str
    summary: dict[str, int]
    details: List[dict[str, Any]]
