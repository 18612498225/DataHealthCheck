# -*- coding: utf-8 -*-
"""
文件名: reports.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 报告 API，获取/下载评估报告（JSON、HTML、PDF）
"""
import io
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import AssessmentResult, Task
from app.services.report_cn import build_report_cn

router = APIRouter()


@router.get("/{task_id}")
def get_report(task_id: str, db: Session = Depends(get_db)):
    ar = db.query(AssessmentResult).filter(AssessmentResult.task_id == task_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="报告未找到")
    det = json.loads(ar.details) if isinstance(ar.details, str) else ar.details
    if isinstance(det, dict) and "summary" in det:
        return {"task_id": task_id, **det}
    return {
        "task_id": task_id,
        "summary": json.loads(ar.summary) if isinstance(ar.summary, str) else ar.summary,
        "details": det,
    }


@router.get("/{task_id}/cn")
def get_report_cn(task_id: str, db: Session = Depends(get_db)):
    """返回符合中国标准(GB/T 36344)的报告 JSON"""
    ar = db.query(AssessmentResult).filter(AssessmentResult.task_id == task_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="报告未找到")
    det = json.loads(ar.details) if isinstance(ar.details, str) else ar.details
    if not isinstance(det, dict) or "details_by_datasource" not in det:
        raise HTTPException(status_code=400, detail="Report format not supported for CN")
    task = db.query(Task).filter(Task.id == task_id).first()
    task_name = task.name if task else "数据质量评估"
    report_cn = build_report_cn(
        det["details_by_datasource"],
        det.get("datasource_names") or {},
        task_name=task_name,
    )
    return {"task_id": task_id, **report_cn}


@router.get("/{task_id}/html", response_class=HTMLResponse)
def get_report_html(task_id: str, db: Session = Depends(get_db)):
    ar = db.query(AssessmentResult).filter(AssessmentResult.task_id == task_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="报告未找到")
    return HTMLResponse(content=ar.report_html or "")


def _html_to_pdf(html: str) -> bytes:
    """将 HTML 转为 PDF 字节流"""
    try:
        from xhtml2pdf import pisa
        buf = io.BytesIO()
        pisa.CreatePDF(html.encode("utf-8"), dest=buf, encoding="utf-8")
        return buf.getvalue()
    except Exception:
        return b""


@router.get("/{task_id}/download")
def download_report(task_id: str, format: str = "html", db: Session = Depends(get_db)):
    """下载报告为 HTML、JSON 或 PDF 文件"""
    ar = db.query(AssessmentResult).filter(AssessmentResult.task_id == task_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="报告未找到")

    if format == "pdf":
        html = ar.report_html or ""
        pdf_bytes = _html_to_pdf(html)
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="PDF generation failed (install xhtml2pdf)")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="report-{task_id}.pdf"'},
        )
    if format == "json":
        det = json.loads(ar.details) if isinstance(ar.details, str) else ar.details
        data = {"task_id": task_id, **det} if isinstance(det, dict) and "summary" in det else {
            "task_id": task_id,
            "summary": json.loads(ar.summary) if isinstance(ar.summary, str) else ar.summary,
            "details": det,
        }
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="report-{task_id}.json"'},
        )
    else:
        html = ar.report_html or ""
        return Response(
            content=html,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="report-{task_id}.html"'},
        )
