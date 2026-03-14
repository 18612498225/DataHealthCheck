# -*- coding: utf-8 -*-
"""
文件名: profiling.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据剖析 API，对数据源执行列级统计与规则推荐
"""
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
        raise HTTPException(status_code=404, detail="数据源未找到")

    config = json.loads(ds.config) if isinstance(ds.config, str) else ds.config
    from app.services.profiling import run_profiling as do_profiling
    result = do_profiling(ds.source_type, config, sample_size=req.sample_size)
    if result is None:
        raise HTTPException(status_code=400, detail="加载数据源失败")
    return result
