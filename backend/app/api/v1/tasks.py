# -*- coding: utf-8 -*-
"""
文件名: tasks.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 任务执行 API，运行评估任务、查看任务列表与详情
"""
import logging
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.models import Datasource, RuleSet, Task, AssessmentResult
from app.schemas.task import TaskRun, TaskResponse
from app.services.assessment import run_assessment
from app.services.report import build_report_json
from app.services.report_cn import build_report_cn, build_report_html_cn
import json

router = APIRouter()


def _resolve_mappings(d: TaskRun) -> list[tuple[str, str, dict | None]]:
    """解析任务配置，返回 (数据源id, 规则集id, 列映射) 列表"""
    if d.datasource_rule_mappings:
        return [
            (
                m["datasource_id"],
                m["rule_set_id"],
                m.get("column_mapping") if isinstance(m.get("column_mapping"), dict) else None,
            )
            for m in d.datasource_rule_mappings
            if m.get("datasource_id") and m.get("rule_set_id")
        ]
    ids = d.datasource_ids or []
    if not ids or not d.rule_set_id:
        return []
    return [(ds_id, d.rule_set_id, None) for ds_id in ids]


@router.post("/run")
def run_task(d: TaskRun, db: Session = Depends(get_db)):
    mappings = _resolve_mappings(d)
    if not mappings:
        raise HTTPException(status_code=400, detail="请选择至少一个数据源并配置规则集")

    logger.info("任务开始: name=%s 数据源数=%d", d.name, len(mappings))
    task = Task(
        name=d.name,
        datasource_id=mappings[0][0],  # legacy NOT NULL; 满足数据库约束
        datasource_ids=json.dumps([m[0] for m in mappings]),
        datasource_rule_mappings=json.dumps([
            {"datasource_id": m[0], "rule_set_id": m[1], "column_mapping": m[2] or {}}
            for m in mappings
        ]),
        rule_set_id=mappings[0][1],
        status="running",
        trigger_type="manual",
        started_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        by_datasource = {}
        ds_names = {}
        for ds_id, rule_set_id, col_map in mappings:
            rs = db.query(RuleSet).filter(RuleSet.id == rule_set_id).first()
            if not rs:
                raise HTTPException(status_code=404, detail=f"规则集 {rule_set_id} 未找到")
            rules = json.loads(rs.rules) if isinstance(rs.rules, str) else rs.rules
            ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
            if not ds:
                raise HTTPException(status_code=404, detail=f"数据源 {ds_id} 未找到")
            config = json.loads(ds.config) if isinstance(ds.config, str) else ds.config
            results, err = run_assessment(ds.source_type, config, rules, column_mapping=col_map)
            if err:
                task.status = "failed"
                task.finished_at = datetime.utcnow()
                db.commit()
                raise HTTPException(status_code=400, detail=f"{ds.name}: {err}")
            by_datasource[ds_id] = results
            ds_names[ds_id] = ds.name

        report = build_report_json([], by_datasource=by_datasource, ds_names=ds_names)
        report["datasource_names"] = ds_names
        report_cn = build_report_cn(by_datasource, ds_names, task_name=d.name)
        report_html = build_report_html_cn(report_cn)

        ar = AssessmentResult(
            task_id=task.id,
            summary=json.dumps(report["summary"]),
            details=json.dumps(report),
            report_html=report_html,
        )
        db.add(ar)
        task.status = "completed"
        task.finished_at = datetime.utcnow()
        db.commit()
        logger.info("任务完成: task_id=%s 数据源数=%d", task.id, len(by_datasource))

        return {
            "task_id": task.id,
            "status": task.status,
            "result": report,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Task run failed: %s", e)
        task.status = "failed"
        task.finished_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


def _task_to_response(m: Task) -> TaskResponse:
    """将任务模型转为 API 响应格式"""
    ids = []
    if m.datasource_ids:
        try:
            ids = json.loads(m.datasource_ids)
        except Exception:
            pass
    if not ids and m.datasource_id:
        ids = [m.datasource_id]
    return TaskResponse(
        id=m.id,
        name=m.name,
        datasource_ids=ids or None,
        rule_set_id=m.rule_set_id,
        status=m.status,
        trigger_type=m.trigger_type,
        created_at=m.created_at.isoformat() if m.created_at else None,
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    items = db.query(Task).order_by(Task.created_at.desc()).limit(50).all()
    return [_task_to_response(m) for m in items]


@router.get("/{id}")
def get_task(id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    ar = db.query(AssessmentResult).filter(AssessmentResult.task_id == id).first()
    result = None
    if ar:
        det = json.loads(ar.details) if isinstance(ar.details, str) else ar.details
        if isinstance(det, dict) and "summary" in det:
            result = det
        else:
            result = {
                "summary": json.loads(ar.summary) if isinstance(ar.summary, str) else ar.summary,
                "details": det if isinstance(det, list) else (json.loads(ar.details) if isinstance(ar.details, str) else ar.details),
            }
    return {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "datasource_ids": json.loads(task.datasource_ids) if task.datasource_ids else ([task.datasource_id] if task.datasource_id else []),
        "result": result,
    }
