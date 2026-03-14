import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Datasource
from app.schemas.datasource import DatasourceCreate, DatasourceUpdate, DatasourceResponse
from app.services.data_loader import load_data

router = APIRouter()


def model_to_response(m: Datasource) -> DatasourceResponse:
    config = json.loads(m.config) if isinstance(m.config, str) else m.config
    return DatasourceResponse(
        id=m.id,
        name=m.name,
        source_type=m.source_type,
        config=config,
        business_scenario=m.business_scenario,
        created_at=m.created_at.isoformat() if m.created_at else None,
        updated_at=m.updated_at.isoformat() if m.updated_at else None,
    )


@router.get("", response_model=list[DatasourceResponse])
def list_datasources(business_scenario: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Datasource)
    if business_scenario:
        q = q.filter(Datasource.business_scenario == business_scenario)
    items = q.all()
    return [model_to_response(m) for m in items]


@router.post("", response_model=DatasourceResponse)
def create_datasource(d: DatasourceCreate, db: Session = Depends(get_db)):
    m = Datasource(
        name=d.name,
        source_type=d.source_type,
        config=json.dumps(d.config),
        business_scenario=d.business_scenario,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return model_to_response(m)


@router.get("/{id}", response_model=DatasourceResponse)
def get_datasource(id: str, db: Session = Depends(get_db)):
    m = db.query(Datasource).filter(Datasource.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Datasource not found")
    return model_to_response(m)


@router.put("/{id}", response_model=DatasourceResponse)
def update_datasource(id: str, d: DatasourceUpdate, db: Session = Depends(get_db)):
    m = db.query(Datasource).filter(Datasource.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Datasource not found")
    if d.name is not None:
        m.name = d.name
    if d.source_type is not None:
        m.source_type = d.source_type
    if d.config is not None:
        m.config = json.dumps(d.config)
    if d.business_scenario is not None:
        m.business_scenario = d.business_scenario
    db.commit()
    db.refresh(m)
    return model_to_response(m)


@router.delete("/{id}")
def delete_datasource(id: str, db: Session = Depends(get_db)):
    m = db.query(Datasource).filter(Datasource.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Datasource not found")
    db.delete(m)
    db.commit()
    return {"ok": True}


@router.post("/{id}/test")
def test_datasource(id: str, db: Session = Depends(get_db)):
    """Test connection / load data from datasource."""
    m = db.query(Datasource).filter(Datasource.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Datasource not found")
    config = json.loads(m.config) if isinstance(m.config, str) else m.config
    df = load_data(m.source_type, config)
    if df is None:
        return {"ok": False, "message": "Failed to load data"}
    return {"ok": True, "message": f"Loaded {len(df)} rows, {len(df.columns)} columns"}
