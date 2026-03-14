from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Datasource
import json

router = APIRouter()


class ProfilingRequest(BaseModel):
    datasource_id: str
    sample_size: int = 10000


@router.post("")
def run_profiling(req: ProfilingRequest, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == req.datasource_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Datasource not found")

    config = json.loads(ds.config) if isinstance(ds.config, str) else ds.config
    from app.services.profiling import run_profiling as do_profiling
    result = do_profiling(ds.source_type, config, sample_size=req.sample_size)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to load datasource")
    return result
