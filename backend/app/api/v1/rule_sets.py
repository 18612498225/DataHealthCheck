from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import RuleSet
from app.schemas.rule_set import RuleSetCreate, RuleSetUpdate, RuleSetResponse
import json

router = APIRouter()


def model_to_response(m: RuleSet) -> RuleSetResponse:
    rules = json.loads(m.rules) if isinstance(m.rules, str) else m.rules
    dims = json.loads(m.quality_dimensions) if m.quality_dimensions and isinstance(m.quality_dimensions, str) else m.quality_dimensions
    return RuleSetResponse(
        id=m.id,
        name=m.name,
        description=m.description,
        rules=rules,
        industry=m.industry,
        quality_dimensions=dims,
        standard_ref=m.standard_ref,
        created_at=m.created_at.isoformat() if m.created_at else None,
        updated_at=m.updated_at.isoformat() if m.updated_at else None,
    )


@router.get("", response_model=list[RuleSetResponse])
def list_rule_sets(industry: str | None = None, db: Session = Depends(get_db)):
    q = db.query(RuleSet)
    if industry:
        q = q.filter(RuleSet.industry == industry)
    items = q.all()
    return [model_to_response(m) for m in items]


@router.post("", response_model=RuleSetResponse)
def create_rule_set(d: RuleSetCreate, db: Session = Depends(get_db)):
    m = RuleSet(
        name=d.name,
        description=d.description,
        rules=json.dumps(d.rules),
        industry=d.industry,
        quality_dimensions=json.dumps(d.quality_dimensions) if d.quality_dimensions else None,
        standard_ref=d.standard_ref,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return model_to_response(m)


@router.get("/{id}", response_model=RuleSetResponse)
def get_rule_set(id: str, db: Session = Depends(get_db)):
    m = db.query(RuleSet).filter(RuleSet.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Rule set not found")
    return model_to_response(m)


@router.put("/{id}", response_model=RuleSetResponse)
def update_rule_set(id: str, d: RuleSetUpdate, db: Session = Depends(get_db)):
    m = db.query(RuleSet).filter(RuleSet.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Rule set not found")
    if d.name is not None:
        m.name = d.name
    if d.description is not None:
        m.description = d.description
    if d.rules is not None:
        m.rules = json.dumps(d.rules)
    if d.industry is not None:
        m.industry = d.industry
    if d.quality_dimensions is not None:
        m.quality_dimensions = json.dumps(d.quality_dimensions) if d.quality_dimensions else None
    if d.standard_ref is not None:
        m.standard_ref = d.standard_ref
    db.commit()
    db.refresh(m)
    return model_to_response(m)


@router.delete("/{id}")
def delete_rule_set(id: str, db: Session = Depends(get_db)):
    m = db.query(RuleSet).filter(RuleSet.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Rule set not found")
    db.delete(m)
    db.commit()
    return {"ok": True}
