from pydantic import BaseModel
from typing import Optional, Any


class DatasourceBase(BaseModel):
    name: str
    source_type: str = "csv"
    config: dict[str, Any]
    business_scenario: Optional[str] = None


class DatasourceCreate(DatasourceBase):
    pass


class DatasourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    business_scenario: Optional[str] = None


class DatasourceResponse(DatasourceBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
